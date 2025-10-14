# client.py
import socket

# Sunucunun IP adresi ve port numarası
HOST = '127.0.0.1'  # Sunucunun IP adresi
PORT = 65432        # Sunucunun port numarası

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
        print("Sunucuya bağlandı. Mesajlaşmaya başlayabilirsiniz.")
        print(":q yazarak çıkış yapabilirsiniz.")
        while True:
            message = input("Sizin mesajınız: ")
            s.sendall(message.encode('utf-8'))
            if message.lower() == ':q':
                break
            
            data = s.recv(1024)
            response = data.decode('utf-8')
            print(f"Sunucudan gelen mesaj: {response}")
            if response.lower() == ':q':
                print("Sunucu bağlantıyı sonlandırdı.")
                break
                
    except ConnectionRefusedError:
        print("Hata: Sunucuya bağlanılamadı. Lütfen sunucunun çalıştığından emin olun.")

print("İstemci programı sonlanıyor. Hoşça kalın!")
