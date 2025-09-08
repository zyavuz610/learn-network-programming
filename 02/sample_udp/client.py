import socket
import random
import time

# Sunucunun IP adresi ve port numarası
HOST = '127.0.0.1'
PORT = 65432

# UDP soketi oluşturma
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    print("Sayılar üretiliyor ve sunucuya gönderiliyor...")
    
    for i in range(10):
        # 10 ile 100 arasında rastgele sayı üretme
        number = random.randint(10, 100)
        
        # Sayıyı stringe dönüştürerek gönderme
        s.sendto(str(number).encode('utf-8'), (HOST, PORT))
        print(f"Gönderildi: {number}")
        
        time.sleep(0.5)  # Gönderimler arasında yarım saniye bekleme
    
    print("Tüm sayılar gönderildi. Sunucuya çıkış mesajı gönderiliyor...")
    
    # Çıkış mesajını gönder
    s.sendto(b':q', (HOST, PORT))
    
    # Sunucudan son toplamı bekleme
    data, server_addr = s.recvfrom(1024)
    response = data.decode('utf-8')
    
    print(f"Sunucudan gelen son mesaj: {response}")

print("İstemci programı sonlandı.")