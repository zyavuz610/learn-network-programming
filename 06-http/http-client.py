# client.py

import socket

# Sunucu ayarları
HOST = '127.0.0.1'  # Sunucunun IP adresi
PORT = 65432        # Sunucunun port numarası

# Socket oluşturma
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Sunucuya bağlan
    s.connect((HOST, PORT))
    print(f"Sunucuya başarıyla bağlandı: {HOST}:{PORT}")
    
    # Gönderilecek mesajı oluştur
    message = "Merhaba, sunucu!"
    
    # Mesajı sunucuya gönder
    s.sendall(message.encode('utf-8'))
    
    # Sunucudan gelen yanıtı al
    data = s.recv(1024)
    
    # Yanıtı ekrana yazdır
    print(f"Sunucudan gelen yanıt: {data.decode('utf-8')}")

print("Bağlantı kapatıldı.")