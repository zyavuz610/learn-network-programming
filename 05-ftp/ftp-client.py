import socket
import re

HOST = '127.0.0.1'  # Sunucu IP adresi
PORT = 21          # Kontrol bağlantısı için standart FTP portu

def get_response(s):
    """Sunucudan gelen yanıtı okur ve döndürür."""
    response = s.recv(1024).decode('utf-8').strip()
    print(f"<<< {response}")
    return response

def send_command(s, cmd):
    """Sunucuya bir komut gönderir."""
    s.send(f'{cmd}\r\n'.encode('utf-8'))
    print(f">>> {cmd}")

def pasv_mode(s):
    """Pasif mod için veri bağlantısı bilgilerini alır ve bağlantı kurar."""
    send_command(s, 'PASV')
    response = get_response(s)

    # Pasif mod yanıtını regex ile ayrıştır
    match = re.search(r'\((.*),(.*),(.*),(.*),(.*),(.*)\)', response)
    if not match:
        print("PASV yanıtı geçersiz.")
        return None

    # Sunucunun gönderdiği IP ve port bilgilerini al
    p_ip = '.'.join(match.groups()[:4])
    p_port = int(match.group(5)) * 256 + int(match.group(6))

    print(f"Pasif IP: {p_ip}, Pasif Port: {p_port}")

    # Veri bağlantısı için yeni bir socket oluştur ve sunucuya bağlan
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect((p_ip, p_port))
    print("Veri bağlantısı başarıyla kuruldu.")

    return data_socket

def list_files(s):
    """Dosya listesi komutunu gönderir ve yanıtı alır."""
    data_socket = pasv_mode(s)
    if not data_socket:
        return

    send_command(s, 'LIST')
    
    # Kontrol bağlantısı üzerinden listeleme yanıtını al
    get_response(s)

    # Veri bağlantısı üzerinden dosya listesini al
    data = data_socket.recv(4096).decode('utf-8')
    print("--- Sunucudan Gelen Dosyalar ---")
    print(data.strip())
    print("------------------------------")
    
    # Veri bağlantısını kapat
    data_socket.close()

    # Transferin tamamlandığını belirten yanıtı al
    get_response(s)

def retrieve_file(s, filename):
    """Belirtilen dosyayı indirir."""
    data_socket = pasv_mode(s)
    if not data_socket:
        return

    send_command(s, f'RETR {filename}')
    
    # Kontrol bağlantısı üzerinden transferin başladığını belirten yanıtı al
    get_response(s)
    
    # Veri bağlantısı üzerinden dosya verisini al
    try:
        with open(f'downloaded_{filename}', 'wb') as f:
            while True:
                data = data_socket.recv(1024)
                if not data:
                    break
                f.write(data)
        print(f"'{filename}' dosyası 'downloaded_{filename}' olarak kaydedildi.")
    except Exception as e:
        print(f"Dosya indirme hatası: {e}")
        
    data_socket.close()
    get_response(s)

def main():
    # Kontrol bağlantısını kur
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print("Kontrol bağlantısı kuruldu.")
    
    get_response(client_socket)
    
    # Örnek komutları çalıştır
    list_files(client_socket)
    retrieve_file(client_socket, 'ftp-server.py') # Bu dosyanın sunucu tarafında olduğundan emin olun
    
    # Oturumu kapat
    send_command(client_socket, 'QUIT')
    get_response(client_socket)
    
    client_socket.close()
    print("Bağlantı kapatıldı.")

if __name__ == "__main__":
    main()