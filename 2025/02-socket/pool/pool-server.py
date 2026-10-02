import socket
import threading
from concurrent.futures import ThreadPoolExecutor

# Sunucu adresi ve portu
HOST = '127.0.0.1'
PORT = 8888

# İş parçacığı havuzu için maksimum işçi sayısı (eş zamanlı bağlantı limiti)
MAX_WORKERS = 5

# Bağlı istemcileri tutmak için bir liste ve kilit
clients = []
clients_lock = threading.Lock()

def broadcast(message, sender_conn):
    """
    Gelen mesajı gönderen hariç tüm bağlı istemcilere gönderir.
    """
    with clients_lock:
        for client_socket in clients:
            if client_socket is not sender_conn:
                try:
                    client_socket.sendall(message.encode('utf-8'))
                except:
                    # İletişim hatası varsa istemciyi kaldır
                    clients.remove(client_socket)
                    client_socket.close()

def handle_client(conn, addr):
    """
    İş parçacığı havuzundaki her iş parçacığının yürüteceği fonksiyon.
    Bir istemci bağlantısını yönetir.
    """
    print(f"İstemci {addr} bağlandı. Toplam aktif iş parçacığı: {threading.active_count()}")
    
    # Yeni istemciyi listeye ekle
    with clients_lock:
        clients.append(conn)

    try:
        while True:
            # İstemciden veri gelene kadar bekle (bu, iş parçacığını bloklar)
            data = conn.recv(1024)
            if not data:
                print(f"İstemci {addr} bağlantıyı kesti.")
                break
            
            message = data.decode('utf-8')
            print(f"[{addr}] Gelen mesaj: {message.strip()}")

            # Gelen mesajı diğer tüm istemcilere gönder (broadcast)
            broadcast(f"[{addr}]: {message.strip()}", conn)

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
    Sunucuyu başlatır ve ThreadPoolExecutor kullanarak bağlantıları yönetir.
    """
    # İş parçacığı havuzunu oluştur
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"Sohbet sunucusu {HOST}:{PORT} adresinde dinliyor...")
            print(f"{MAX_WORKERS} adet iş parçacığı hazır bekliyor.")
            
            while True:
                conn, addr = server_socket.accept() # Yeni bağlantıyı kabul et
                
                # Yeni istemci için işi havuza gönder
                executor.submit(handle_client, conn, addr)
                print(f"İstemci bağlantısı havuzdaki bir iş parçacığına atandı.")

if __name__ == "__main__":
    start_server()