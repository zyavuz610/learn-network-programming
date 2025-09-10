import socket

# Sunucunun IP adresi ve port numarası
HOST = '127.0.0.1'
PORT = 65432

# UDP soketi oluşturma
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    print("Mesajlaşmaya başlayabilirsiniz.")
    print(":q yazarak çıkış yapabilirsiniz.")
    
    while True:
        message = input("Sizin mesajınız: ")
        
        # Sunucuya mesajı ve sunucunun adresini gönder
        s.sendto(message.encode('utf-8'), (HOST, PORT))
        
        if message.lower() == ':q':
            break
            
        # Sunucudan yanıt bekleme
        data, server_addr = s.recvfrom(1024)
        response = data.decode('utf-8')
        
        print(f"Sunucudan gelen mesaj: {response}")
        
        if response.lower() == ':q':
            print("Sunucu bağlantıyı sonlandırdı.")
            break

print("İstemci programı sonlanıyor. Hoşça kalın!")