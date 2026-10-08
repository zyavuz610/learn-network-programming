# Ağ iletişimi için gerekli soket modülünü içeri aktar
import socket

# Bağlanılacak sunucunun IP adresi ve port numarası
HOST = '127.0.0.1'  # Sunucu yerel makinede (localhost) çalışıyor
PORT = 65432        # Sunucunun dinlediği port numarası

# TCP/IP soketi oluştur:
# - socket.AF_INET: IPv4 protokolünü belirtir
# - socket.SOCK_STREAM: Güvenilir ve sıralı veri aktarımı sağlayan TCP protokolü
# 'with' bloğu işlem tamamlandığında soketin otomatik kapanmasını garanti eder
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    # Belirtilen IP ve porttaki sunucuya bağlantı isteği gönder
    client_socket.connect((HOST, PORT))
    print("Sunucuya bağlandı. Mesajınızı yazın (çıkış için 'q'):")
    
    # Karşılıklı mesajlaşma döngüsü
    while True:
        # Kullanıcıdan gönderilecek mesajı terminalden al
        message = input("İstemci mesajı: ")
        
        # Kullanıcı 'q' veya 'Q' yazarsa döngüyü kır ve bağlantıyı sonlandır
        if message.lower() == 'q':
            break
            
        # Metni UTF-8 formatında bayt dizisine dönüştürerek sunucuya gönder
        client_socket.sendall(message.encode('utf-8'))
        
        # Sunucudan gelen cevabı en fazla 1024 bayt olarak oku
        data = client_socket.recv(1024)
        
        # Gelen bayt verisini UTF-8 metne çevirip ekrana yazdır
        print(f"Sunucu: {data.decode('utf-8')}")