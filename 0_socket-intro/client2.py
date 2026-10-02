import socket

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    print("Sunucuya bağlandı. Mesajınızı yazın (çıkış için 'q'):")
    while True:
        message = input("İstemci mesajı: ")
        if message.lower() == 'q':
            break
        client_socket.sendall(message.encode('utf-8'))
        data = client_socket.recv(1024)
        print(f"Sunucu: {data.decode('utf-8')}")
