# Gerekli modülü içeri aktar
import socket

# Sunucu bilgilerini tanımla
HOST = '127.0.0.1'  # Yerel ağ adresi (localhost)
PORT = 65432        # Bağlantı noktası, 1024'ten büyük olmalı

# TCP soketi oluştur
# AF_INET: IPv4 adresi ailesi
# SOCK_STREAM: TCP protokolü
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Soketi belirtilen IP ve porta bağla
    s.bind((HOST, PORT))
    
    # Gelen bağlantıları dinlemeye başla (1 bağlantı sıraya alınabilir)
    s.listen()
    
    print(f"Sunucu {HOST}:{PORT} adresinde dinliyor...")
    
    # Gelen bir bağlantıyı kabul et
    # conn: yeni bağlantı için soket nesnesi
    # addr: istemcinin adresi (IP, port)
    conn, addr = s.accept()
    
    # İstemci ile iletişim için bir "with" bloğu oluştur
    with conn:
        print(f"Bağlantı adresi: {addr}")
        
        # Veri alışverişi döngüsü
        while True:
            # İstemciden veri al (1024 bayt boyutunda)
            data = conn.recv(1024)
            
            # Eğer veri yoksa (bağlantı kapatılmışsa), döngüyü sonlandır
            if not data:
                break
                
            # Alınan veriyi geri gönder
            conn.sendall(data)
            
# "with" bloğu sayesinde soketler otomatik olarak kapatılır
print("Sunucu kapatıldı.")