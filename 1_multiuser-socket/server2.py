import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

clients = []

def broadcast(message, current_client):
    for client in clients:
        if client != current_client:
            try:
                client.sendall(message)
            except:
                client.close()
                if client in clients:
                    clients.remove(client)

def handle_client(client_socket, client_address):
    print(f"Yeni bağlantı: {client_address}")
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            broadcast(message, client_socket)
        except:
            break
    print(f"Bağlantı kesildi: {client_address}")
    if client_socket in clients:
        clients.remove(client_socket)
    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Çoklu istemci sunucusu {HOST}:{PORT} üzerinde dinliyor...")
    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    start_server()
