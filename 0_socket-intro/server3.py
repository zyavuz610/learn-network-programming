import socket

HOST = '127.0.0.1'
PORT = 65432

# Toplamda sırayla kabul edilecek istemci sayısı
TOTAL_CLIENTS = 2

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Sunucu {HOST}:{PORT} üzerinde dinleniyor...")
    print(f"Sırayla {TOTAL_CLIENTS} istemci kabul edilecek (Thread kullanılmıyor).\n")

    # İstemcileri sırayla kabul eden döngü (1'den 2'ye kadar)
    for client_num in range(1, TOTAL_CLIENTS + 1):
        print(f"--> İstemci {client_num} bekleniyor...")
        conn, addr = server_socket.accept()
        
        with conn:
            print(f"--> İstemci {client_num} bağlandı! (Adres: {addr})")
            
            while True:
                data = conn.recv(1024)
                
                # İstemci soketi aniden kapattıysa
                if not data:
                    print(f"İstemci {client_num} bağlantıyı kapattı.")
                    break
                
                message = data.decode('utf-8')
                
                # İstemci 'q' gönderdiyse bağlantıyı sonlandır
                if message.lower() == 'q':
                    print(f"İstemci {client_num} 'q' gönderdi, bağlantı sonlandırılıyor.")
                    break
                
                # Gelen mesajı hangi istemciden geldiğini belirterek yazdır
                print(f"[Gelen - İstemci {client_num} ({addr})]: {message}")
                
                # Sunucu cevabını hangi istemciye yazıldığını belirten prompt ile al
                reply = input(f"[Giden - İstemci {client_num}'e Mesaj]: ")
                conn.sendall(reply.encode('utf-8'))
        
        print(f"<-- İstemci {client_num} ile iletişim bitti.\n")

print(f"Belirlenen {TOTAL_CLIENTS} istemci ile işlemler tamamlandı. Sunucu kapatılıyor.")
