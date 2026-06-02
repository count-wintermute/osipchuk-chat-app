
import socket
import threading

HOST = '0.0.0.0'  
PORT = 5555         

clients = [] # 
nicknames = {} 

def broadcast(message, sender_socket):
    """Sends a message to every client except the one who sent it."""
    for client_socket in clients:
        
        if client_socket != sender_socket:
            try:
                client_socket.sendall(message + b'\n')
            except Exception as e:
                print(f"Error sending to a client: {e}")

def handle_client(client_socket, nickname):
    """Handles all communication with a single connected client."""
    print(f"[*] New user connected: {nickname}")

   
    welcome_msg = f"[SERVER] {nickname} has joined the chat."
    broadcast(welcome_msg.encode('utf-8'), client_socket)

    while True:
        try:
            
            message = client_socket.recv(1024)
            if not message:
                break
            
            
            full_message = message.decode('utf-8').strip()
            print(f"<{nickname}>: {full_message}")

            
            formatted_msg = f"[{nickname}]: {full_message}"
            broadcast(formatted_msg.encode('utf-8'), client_socket)

        except ConnectionResetError:
            print("\n[!] Client forcibly disconnected.")
            break
        except Exception as e:
            print(f"\n[!] Error handling client: {e}")
            break

    
    index = clients.index(client_socket)
    clients.pop(index)
    del nicknames[client_socket]
    disconnect_msg = f"[SERVER] {nickname} has left the chat."
    broadcast(disconnect_msg.encode('utf-8'), client_socket)
    print(f"[-] {nickname} disconnected.")


def start_server():
    """Initializes and starts the socket server."""
    global clients, nicknames
    
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print("=========================================")
        print(f"[*] Chat Server is running on {HOST}:{PORT}")
        print("=========================================\n")
    except socket.error as e:
        print(f"[FATAL] Could not bind to port {PORT}. Is it already in use? Error: {e}")
        return

    while True:
        try:
            
            client_socket, client_address = server_socket.accept()
            
            
            
            initial_message = client_socket.recv(1024).decode('utf-8').strip()
            if not initial_message:
                continue

            
            nickname = initial_message 
            
            clients.append(client_socket)
            nicknames[client_socket] = nickname
            
            
            thread = threading.Thread(target=handle_client, args=(client_socket, nickname))
            thread.start()

        except KeyboardInterrupt:
            print("\n[*] Server shutting down...")
            server_socket.close()
            break
        except Exception as e:
            print(f"[CRITICAL ERROR] {e}")


if __name__ == "__main__":
    start_server()
