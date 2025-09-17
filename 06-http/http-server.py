# server.py

import socket

# Sunucu ayarları
HOST = '127.0.0.1'  # Yerel ağ adresi (localhost)
PORT = 65432        # Bağlanılacak port numarası (1024'ten büyük olmalı)

# Socket oluşturma
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Soketi belirtilen IP ve porta bağla
    s.bind((HOST, PORT))
    
    # Gelen bağlantıları dinle
    s.listen()
    print(f"Sunucu {HOST}:{PORT} adresinde dinliyor...")
    
    # Bağlantıyı kabul et
    conn, addr = s.accept()
    
    with conn:
        print(f"Bağlantı adresi: {addr}")
        
        while True:
            # İstemciden veri al
            data = conn.recv(1024) # 1024 baytlık tampon boyutu
            
            # Eğer veri yoksa veya bağlantı kapandıysa döngüden çık
            if not data:
                break
                
            # Alınan veriyi ekrana yazdır
            print(f"İstemciden gelen mesaj: {data.decode('utf-8')}")
            
            # Gelen mesaja yanıt oluştur ve gönder
            response_message = "Sunucudan yanıt: Mesajınız alındı!"
            conn.sendall(response_message.encode('utf-8'))

print("Bağlantı kapatıldı.")