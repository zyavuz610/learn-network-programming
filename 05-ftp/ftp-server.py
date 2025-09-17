import socket
import os
import random

HOST = '127.0.0.1'  # Dinlenecek IP adresi
PORT = 21          # Kontrol bağlantısı için standart FTP portu

def start_server():
    """FTP sunucusunu başlatır."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Sunucu {HOST}:{PORT} adresinde dinliyor...")
    print(">> Bağlantılar bekleniyor...")

    while True:
        conn, addr = server_socket.accept()
        print(f"{addr} adresinden yeni bir bağlantı geldi.")
        print(f"IP adresi: {addr[0]}, Port: {addr[1]}")
        conn.send(b'220 FTP Sunucusuna Hosgeldiniz.\r\n')
        handle_client(conn)

def handle_client(conn):
    """Gelen istemci bağlantısını yönetir."""
    # Kontrol bağlantısı komutlarını dinle
    while True:
        try:
            command = conn.recv(1024).decode('utf-8').strip().upper()
            if not command:
                break

            print(f"Gelen komut: {command}")
            
            if command == 'PASV':
                handle_pasv(conn)
            elif command.startswith('LIST'):
                handle_list(conn)
            elif command.startswith('RETR'):
                handle_retr(conn, command.split(' ')[1])
            elif command == 'QUIT':
                conn.send(b'221 Gule Gule.\r\n')
                break
            else:
                conn.send(b'502 Komut Gecerli Degil.\r\n')
        except (ConnectionResetError, IndexError):
            print("Bağlantı kesildi.")
            break
    
    conn.close()

def handle_pasv(conn):
    """Pasif mod veri bağlantısını ayarlar."""
    # Rastgele bir port seç ve bu portta veri bağlantısı için dinlemeye başla
    data_port = random.randint(49152, 65535) # Dinamik port aralığı
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.bind((HOST, data_port))
    data_socket.listen(1)
    
    # Sunucu IP ve portu, FTP'nin istediği formatta istemciye gönderilir
    # IP adresi ve port numarası virgüllerle ayrılır. Portun son iki hanesi ayrı yazılır.
    # Örnek: '127.0.0.1' -> '127,0,0,1'
    # Örnek: '50000' -> '195,160' (50000 = 256*195 + 160)
    h1, h2, h3, h4 = HOST.split('.')
    p1 = data_port // 256
    p2 = data_port % 256
    
    conn.send(f'227 Entering Passive Mode ({h1},{h2},{h3},{h4},{p1},{p2}).\r\n'.encode('utf-8'))
    print(f"Pasif mod veri bağlantısı için {data_port} portunda bekleniyor.")
    
    # İstemciden veri bağlantısı gelmesini bekle ve bağlantıyı döndür
    data_conn, data_addr = data_socket.accept()
    print(f"Veri bağlantısı {data_addr} adresinden kuruldu.")
    
    # Bağlantıyı global bir değişkene kaydet (daha iyi bir yaklaşım için sınıf kullanılabilir)
    global data_connection
    data_connection = data_conn

def handle_list(conn):
    """Dosya listesini gönderir."""
    # Listeleme işlemi için veri bağlantısının kurulmuş olması beklenir
    try:
        if 'data_connection' not in globals() or not data_connection:
            conn.send(b'425 Veri baglantisi yok.\r\n')
            return

        files = os.listdir('.')
        list_string = '\r\n'.join(files) + '\r\n'
        data_connection.send(list_string.encode('utf-8'))
        conn.send(b'226 Transfer tamamlandi.\r\n')
        
    finally:
        # Veri transferi bittikten sonra bağlantıyı kapat
        if 'data_connection' in globals():
            data_connection.close()
            del globals()['data_connection']

def handle_retr(conn, filename):
    """Belirtilen dosyayı gönderir."""
    try:
        if 'data_connection' not in globals() or not data_connection:
            conn.send(b'425 Veri baglantisi yok.\r\n')
            return
            
        if not os.path.exists(filename):
            conn.send(b'550 Dosya bulunamadi.\r\n')
            return
            
        conn.send(b'150 Dosya transferi basliyor.\r\n')
        with open(filename, 'rb') as f:
            data_connection.sendall(f.read())
            
        conn.send(b'226 Transfer tamamlandi.\r\n')
        
    except Exception as e:
        conn.send(f'550 Hata olustu: {e}\r\n'.encode('utf-8'))

    finally:
        if 'data_connection' in globals():
            data_connection.close()
            del globals()['data_connection']

if __name__ == "__main__":
    start_server()