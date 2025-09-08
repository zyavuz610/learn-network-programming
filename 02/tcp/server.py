import socket

# Sunucunun IP adresi ve port numarası
HOST = '127.0.0.1'  # Yerel makine
PORT = 65432        # 1024'ün üstündeki boş bir port

# socket.AF_INET: Adress Family IPv4
# socket.AF_INET6: Adress Family IPv6
#---
# socket.SOCK_STREAM: TCP kullanımı
# socket.SOCK_DGRAM: UDP kullanımı
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Sunucu {HOST}:{PORT} adresinde dinliyor...")
    conn, addr = s.accept()
    with conn:
        print(f"İstemci {addr} bağlandı.")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(f"İstemciden gelen mesaj: {message}")
            if message.lower() == ':q':
                print("İstemci bağlantıyı sonlandırdı.")
                break
            
            # Sunucudan istemciye yanıt gönderme
            response = input("Sizin mesajınız: ")
            conn.sendall(response.encode('utf-8'))
            if response.lower() == ':q':
                print("Sunucu bağlantıyı sonlandırdı.")
                break

print("Sunucu programı sonlanıyor. Hoşça kalın!")