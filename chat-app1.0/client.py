
import socket
import threading
import sys
from urllib import request 
def get_public_ip():
    """Fetches the public-facing IP address by querying an external service."""
    print("[*] Attempting to retrieve public IP address...")
    try:
       
        with request.urlopen('https://api64.ipify.org') as response:
            ip_address = response.read().decode('utf-8').strip()
            return ip_address

PORT = 5555

def receive_messages(client_socket):
    """Thread function to continuously listen and print incoming server messages."""
    print("\n[--- Connected ---]\n")
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8').strip()

            if message == "NICK":
                break
            elif message:
                print(f"\n{message}") 
                
                sys.stdout.write("> ") 
                sys.stdout.flush()

        except ConnectionResetError:
            print("\n[!] Disconnected from the server.")
            break
        except Exception as e:
            print(f"\n[!!!] An error occurred in receiving thread: {e}")
            break

def start_client():
    """Initializes connection and handles sending messages."""
    
    
    nickname = input("Please choose your nickname: ").strip()
    if not nickname:
        print("Nickname cannot be empty. Exiting.")
        return

    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"[*] Attempting to connect to {HOST}:{PORT}...")
        client_socket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("\n[!!!] Could not connect. Is the server running?")
        return

    
    
    client_socket.sendall(nickname.encode('utf-8'))
    print(f"\n[SUCCESS] Logged in as {nickname}! Start chatting.")

    
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    
    while True:
        try:
            message_input = input("> ").strip()
            if not message_input:
                continue
            
            if message_input.lower() == 'exit':
                break
            
            
            client_socket.sendall(f"{nickname} {message_input}".encode('utf-8'))

        except EOFError:
            
            print("\n[!!!] Sending exit command...")
            break
        except Exception as e:
            print(f"\n[!!!] An error occurred during sending: {e}")
            break

    
    client_socket.close()
    print("[*] Chat client disconnected.")


if __name__ == "__main__":
    start_client()
