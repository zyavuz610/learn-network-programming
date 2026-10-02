import socket

# Sunucu adresi ve portu
HOST = '127.0.0.1'
PORT = 8888

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
        print("Sunucuya bağlandı. Mesajlaşmaya başlayabilirsiniz.")
        
        while True:
            # Kullanıcıdan mesajı al ve sunucuya gönder
            message = input("Sizin mesajınız: ")
            s.sendall(message.encode('utf-8'))
            
            if message.lower() == ':q':
                break
                
            # Sunucudan gelen yanıtı al
            data = s.recv(1024)
            if not data:
                break
            print(f"Gelen mesaj: {data.decode('utf-8')}")

    except ConnectionRefusedError:
        print("Hata: Sunucuya bağlanılamadı. Lütfen sunucunun çalıştığından emin olun.")

print("İstemci programı sonlandı.")