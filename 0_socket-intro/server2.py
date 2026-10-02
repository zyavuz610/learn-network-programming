import socket

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Sunucu {HOST}:{PORT} üzerinde dinleniyor...")
    conn, addr = server_socket.accept()
    with conn:
        print(f"Bağlantı sağlandı: {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"İstemci: {data.decode('utf-8')}")
            reply = input("Sunucu mesajı: ")
            conn.sendall(reply.encode('utf-8'))
