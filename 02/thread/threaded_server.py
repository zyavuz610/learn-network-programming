import socket
import threading

# Sunucu adresi ve portu
HOST = '127.0.0.1'
PORT = 8888

# Bağlı istemcileri tutmak için bir liste
clients = []
clients_lock = threading.Lock() # Listeye erişim için kilit

def handle_client(conn, addr):
    """
    Her bir istemci bağlantısını ayrı bir iş parçacığında yönetir.
    """
    print(f"İstemci {addr} bağlandı.")
    
    # Yeni istemciyi listeye ekle
    with clients_lock:
        clients.append(conn)

    try:
        while True:
            # İstemciden veri gelene kadar bekle
            data = conn.recv(1024)
            if not data:
                print(f"İstemci {addr} bağlantıyı kesti.")
                break
            
            message = data.decode('utf-8')
            print(f"[{addr}] Gelen mesaj: {message.strip()}")

            # Gelen mesajı diğer tüm istemcilere gönder (broadcast)
            with clients_lock:
                for client_socket in clients:
                    # Mesajı gönderen istemciye geri gönderme
                    if client_socket is not conn:
                        try:
                            client_socket.sendall(f"[{addr}]: {message.strip()}".encode('utf-8'))
                        except:
                            # Hata oluşursa istemciyi listeden çıkar
                            clients.remove(client_socket)
                            client_socket.close()

    except ConnectionResetError:
        print(f"İstemci {addr} aniden bağlantıyı kesti.")
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        # İstemci çıkış yapınca bağlantısını kapat ve listeden çıkar
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"Bağlantı {addr} için sonlandırıldı.")

def start_server():
    """
    Sunucuyu başlatır ve gelen bağlantılar için thread'ler oluşturur.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Sohbet sunucusu {HOST}:{PORT} adresinde dinliyor...")
        
        while True:
            conn, addr = server_socket.accept() # Yeni bir bağlantıyı kabul et
            
            # Her yeni bağlantı için ayrı bir thread oluştur
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True # Ana program kapandığında thread'lerin de kapanmasını sağlar
            thread.start() # Thread'i başlat

if __name__ == "__main__":
    start_server()