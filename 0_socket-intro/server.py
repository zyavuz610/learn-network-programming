# Ağ iletişimi için gerekli soket modülünü içeri aktar
import socket

# Sunucunun çalışacağı IP adresi ve port numarası
HOST = '127.0.0.1'  # Localhost (yerel makine)
PORT = 65432        # İletişim için kullanılacak port (1024'ten büyük standart dışı port)

# TCP/IP soketi oluştur:
# - socket.AF_INET: IPv4 protokolünü belirtir
# - socket.SOCK_STREAM: Bağlantı tabanlı TCP protokolünü belirtir
# 'with' bloğu işlem bittiğinde soketin otomatik ve güvenli bir şekilde kapatılmasını sağlar
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Soketi belirtilen IP ve porta bağla
    server_socket.bind((HOST, PORT))
    
    # Sunucuyu dinleme moduna al (gelen bağlantı isteklerini kabul etmeye başla)
    server_socket.listen()
    print(f"Sunucu {HOST}:{PORT} üzerinde dinleniyor...")
    
    # Bir istemci bağlanana kadar burada beklenir (bloklayıcı çağrı)
    # conn: İstemciyle haberleşmeyi sağlayacak yeni soket nesnesi
    # addr: Bağlanan istemcinin IP adresi ve port bilgisi
    conn, addr = server_socket.accept()
    
    # İstemci soketini 'with' bloğuna alarak iş bitince otomatik kapanmasını sağla
    with conn:
        print(f"Bağlantı sağlandı: {addr}")
        
        # Karşılıklı veri alışverişi döngüsü
        while True:
            # İstemciden en fazla 1024 bayt veri bekle ve oku
            data = conn.recv(1024)
            
            # İstemci bağlantıyı sonlandırdıysa (boş veri geldiyse) döngüden çık
            if not data:
                break
                
            # Gelen bayt (bytes) tipindeki veriyi metne (string) çevirerek ekrana yazdır
            print(f"İstemci: {data.decode('utf-8')}")
            
            # Sunucu tarafından istemciye gönderilecek cevabı terminalden al
            reply = input("Sunucu mesajı: ")
            
            # Cevap metnini UTF-8 formatında baytlara dönüştürerek istemciye gönder
            conn.sendall(reply.encode('utf-8'))

