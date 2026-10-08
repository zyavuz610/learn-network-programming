import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print("\n" + message)
        except:
            print("Sunucu ile bağlantı kesildi.")
            break

def start_client():
    nickname = input("Kullanıcı adınızı girin: ")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()

    print("Sohbete katıldınız. Mesajınızı yazın (çıkış için 'q'):")
    while True:
        message = input()
        if message.lower() == 'q':
            break
        full_message = f"{nickname}: {message}"
        client_socket.sendall(full_message.encode('utf-8'))

    client_socket.close()

if __name__ == "__main__":
    start_client()
