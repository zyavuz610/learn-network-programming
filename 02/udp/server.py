"""
TCP'de olduğu gibi connect(), listen() veya accept() fonksiyonları kullanılmaz. 
İletişim, veri paketlerinin doğrudan gönderilip alınmasıyla gerçekleşir.
"""
import socket

# Sunucunun IP adresi ve port numarası
HOST = '127.0.0.1'
PORT = 65432

# UDP soketi oluşturma
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"Sunucu {HOST}:{PORT} adresinde dinliyor...")
    
    while True:
        # İstemciden mesaj ve adresi al
        data, addr = s.recvfrom(1024)
        message = data.decode('utf-8')
        
        print(f"İstemci {addr} adresinden gelen mesaj: {message}")
        
        if message.lower() == ':q':
            print("İstemci bağlantıyı sonlandırdı.")
            break
        
        # Sunucudan istemciye yanıt gönderme
        response = input("Sizin mesajınız: ")
        s.sendto(response.encode('utf-8'), addr)
        
        if response.lower() == ':q':
            print("Sunucu bağlantıyı sonlandırdı.")
            break

print("Sunucu programı sonlanıyor. Hoşça kalın!")