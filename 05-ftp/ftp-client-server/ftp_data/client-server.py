STOR dnm.txt
# FTP Server
import socket
import threading
import os
import time

class FTPServer:
    def __init__(self, host='localhost', port=21, root_dir='ftp_server'):
        self.host = host
        self.port = port
        self.root_dir = root_dir
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Sunucu kök dizinini oluştur
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
    
    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"FTP Server {self.host}:{self.port} adresinde başlatıldı")
        print(f"Kök dizin: {os.path.abspath(self.root_dir)}")
        
        while True:
            client_socket, address = self.socket.accept()
            print(f"Bağlantı kabul edildi: {address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
    
    def handle_client(self, client_socket):
        current_dir = self.root_dir
        
        # Karşılama mesajı gönder
        client_socket.send("220 FTP Server Hazır\r\n".encode())
        
        while True:
            try:
                data = client_socket.recv(1024).decode().strip()
                if not data:
                    break
                
                print(f"Komut alındı: {data}")
                
                if data.upper().startswith('USER'):
                    client_socket.send("331 Kullanıcı adı tamam, şifre gerekli\r\n".encode())
                
                elif data.upper().startswith('PASS'):
                    client_socket.send("230 Giriş başarılı\r\n".encode())
                
                elif data.upper() == 'PWD':
                    rel_path = os.path.relpath(current_dir, self.root_dir)
                    if rel_path == '.':
                        rel_path = '/'
                    else:
                        rel_path = '/' + rel_path.replace('\\', '/')
                    client_socket.send(f"257 \"{rel_path}\" mevcut dizin\r\n".encode())
                
                elif data.upper().startswith('CWD'):
                    path = data.split(' ', 1)[1] if len(data.split(' ')) > 1 else ''
                    new_dir = os.path.join(current_dir, path)
                    if os.path.exists(new_dir) and os.path.isdir(new_dir):
                        current_dir = os.path.abspath(new_dir)
                        client_socket.send("250 Dizin değiştirildi\r\n".encode())
                    else:
                        client_socket.send("550 Dizin bulunamadı\r\n".encode())
                
                elif data.upper() == 'LIST':
                    file_list = self.get_file_list(current_dir)
                    response = "150 Dosya listesi gönderiliyor\r\n"
                    response += file_list
                    response += "226 Liste gönderimi tamamlandı\r\n"
                    client_socket.send(response.encode())
                
                elif data.upper().startswith('RETR'):
                    filename = data.split(' ', 1)[1] if len(data.split(' ')) > 1 else ''
                    filepath = os.path.join(current_dir, filename)
                    if os.path.exists(filepath) and os.path.isfile(filepath):
                        try:
                            with open(filepath, 'rb') as f:
                                file_data = f.read()
                            client_socket.send("150 Dosya gönderiliyor\r\n".encode())
                            client_socket.send(f"DATA:{len(file_data)}:".encode())
                            client_socket.send(file_data)
                            client_socket.send("\r\n226 Dosya gönderimi tamamlandı\r\n".encode())
                        except Exception as e:
                            client_socket.send(f"550 Dosya okunamadı: {str(e)}\r\n".encode())
                    else:
                        client_socket.send("550 Dosya bulunamadı\r\n".encode())
                
                elif data.upper().startswith('STOR'):
                    filename = data.split(' ', 1)[1] if len(data.split(' ')) > 1 else ''
                    filepath = os.path.join(current_dir, filename)
                    client_socket.send("150 Dosya yükleme hazır\r\n".encode())
                    
                    # Dosya verisini bekle
                    file_data = b""
                    while True:
                        chunk = client_socket.recv(4096)
                        if chunk.endswith(b"\r\nEND\r\n"):
                            file_data += chunk[:-7]  # END marker'ı çıkar
                            break
                        file_data += chunk
                    
                    try:
                        with open(filepath, 'wb') as f:
                            f.write(file_data)
                        client_socket.send("226 Dosya yükleme tamamlandı\r\n".encode())
                    except Exception as e:
                        client_socket.send(f"550 Dosya yazılamadı: {str(e)}\r\n".encode())
                
                elif data.upper() == 'QUIT':
                    client_socket.send("221 Güle güle\r\n".encode())
                    break
                
                else:
                    client_socket.send("502 Komut desteklenmiyor\r\n".encode())
            
            except Exception as e:
                print(f"Hata: {e}")
                break
        
        client_socket.close()
    
    def get_file_list(self, directory):
        file_list = ""
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    file_list += f"drwxr-xr-x 2 user user 4096 {time.ctime(os.path.getmtime(item_path))} {item}\r\n"
                else:
                    size = os.path.getsize(item_path)
                    file_list += f"-rw-r--r-- 1 user user {size} {time.ctime(os.path.getmtime(item_path))} {item}\r\n"
        except Exception as e:
            file_list = f"Hata: {str(e)}\r\n"
        
        return file_list


# FTP Client
class FTPClient:
    def __init__(self):
        self.socket = None
        self.connected = False
    
    def connect(self, host='localhost', port=21):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            response = self.socket.recv(1024).decode()
            print(f"Server: {response.strip()}")
            self.connected = True
            return True
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            return False
    
    def login(self, username="user", password="pass"):
        if not self.connected:
            print("Önce sunucuya bağlanın!")
            return False
        
        # Kullanıcı adı gönder
        self.socket.send(f"USER {username}\r\n".encode())
        response = self.socket.recv(1024).decode()
        print(f"Server: {response.strip()}")
        
        # Şifre gönder
        self.socket.send(f"PASS {password}\r\n".encode())
        response = self.socket.recv(1024).decode()
        print(f"Server: {response.strip()}")
        
        return "230" in response
    
    def pwd(self):
        if not self.connected:
            print("Önce sunucuya bağlanın!")
            return
        
        self.socket.send("PWD\r\n".encode())
        response = self.socket.recv(1024).decode()
        print(f"Server: {response.strip()}")
    
    def cwd(self, directory):
        if not self.connected:
            print("Önce sunucuya bağlanın!")
            return
        
        self.socket.send(f"CWD {directory}\r\n".encode())
        response = self.socket.recv(1024).decode()
        print(f"Server: {response.strip()}")
    
    def list_files(self):
        if not self.connected:
            print("Önce sunucuya bağlanın!")
            return
        
        self.socket.send("LIST\r\n".encode())
        response = self.socket.recv(4096).decode()
        print("Dosya listesi:")
        print(response)
    
    def download(self, filename, local_path=None):
        if not self.connected:
            print("Önce sunucuya bağlanın!")
            return
        
        if local_path is None:
            local_path = filename
        
        self.socket.send(f"RETR {filename}\r\n".encode())
        
        # İlk yanıtı al
        response = self.socket.recv(1024).decode()
        print(f"Server: {response.strip()}")
        
        if "150" in response:
            # Dosya verisini al
            data = b""
            while True:
                chunk = self.socket.recv(4096)
                if chunk.startswith(b"DATA:"):
                    # Veri boyutunu çıkar
                    header_end = chunk.find(b":")
                    size_end = chunk.find(b":", header_end + 1)
                    size = int(chunk[5:size_end])
                    data = chunk[size_end + 1:]
                    
                    # Kalan veriyi al
                    while len(data) < size:
                        data += self.socket.recv(4096)
                    
                    # Dosyayı kaydet
                    try:
                        with open(local_path, 'wb') as f:
                            f.write(data[:size])
                        print(f"Dosya '{filename}' başarıyla '{local_path}' olarak kaydedildi")
                    except Exception as e:
                        print(f"Dosya kaydetme hatası: {e}")
                    break
            
            # Son yanıtı al
            final_response = self.socket.recv(1024).decode()
            print(f"Server: {final_response.strip()}")
    
    def upload(self, local_file, remote_name=None):
        if not self.connected:
            print("Önce sunucuya bağlanın!")
            return
        
        if remote_name is None:
            remote_name = os.path.basename(local_file)
        
        if not os.path.exists(local_file):
            print(f"Dosya bulunamadı: {local_file}")
            return
        
        try:
            with open(local_file, 'rb') as f:
                file_data = f.read()
            
            self.socket.send(f"STOR {remote_name}\r\n".encode())
            response = self.socket.recv(1024).decode()
            print(f"Server: {response.strip()}")
            
            if "150" in response:
                # Dosya verisini gönder
                self.socket.send(file_data)
                self.socket.send(b"\r\nEND\r\n")
                
                # Son yanıtı al
                final_response = self.socket.recv(1024).decode()
                print(f"Server: {final_response.strip()}")
        
        except Exception as e:
            print(f"Dosya yükleme hatası: {e}")
    
    def quit(self):
        if self.connected:
            self.socket.send("QUIT\r\n".encode())
            response = self.socket.recv(1024).decode()
            print(f"Server: {response.strip()}")
            self.socket.close()
            self.connected = False


# Test ve Kullanım Örneği
def test_ftp():
    # Test dosyası oluştur
    test_dir = "ftp_server"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    with open(os.path.join(test_dir, "test.txt"), "w", encoding="utf-8") as f:
        f.write("Bu bir test dosyasıdır.\nFTP server test için oluşturulmuştur.")
    
    print("Test dosyası oluşturuldu: ftp_server/test.txt")
    
    # Server'ı ayrı bir thread'de başlat
    server = FTPServer()
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    # Server'ın başlaması için bekle
    time.sleep(1)
    
    # Client test
    print("\n" + "="*50)
    print("FTP CLIENT TEST")
    print("="*50)
    
    client = FTPClient()
    
    # Bağlan
    if client.connect():
        print("Sunucuya bağlandı!")
        
        # Giriş yap
        if client.login():
            print("Giriş başarılı!")
            
            # Mevcut dizini göster
            client.pwd()
            
            # Dosyaları listele
            client.list_files()
            
            # Dosya indir
            client.download("test.txt", "downloaded_test.txt")
            
            # Test upload için yeni dosya oluştur
            with open("upload_test.txt", "w", encoding="utf-8") as f:
                f.write("Bu dosya client tarafından yüklendi!")
            
            # Dosya yükle
            client.upload("upload_test.txt")
            
            # Tekrar listele
            print("\nYükleme sonrası dosya listesi:")
            client.list_files()
            
            # Çıkış
            client.quit()
    
    print("\nTest tamamlandı!")


if __name__ == "__main__":
    print("FTP Server-Client Programı")
    print("1. test_ftp() - Otomatik test çalıştır")
    print("2. Manuel kullanım için:")
    print("   - Server: server = FTPServer(); server.start()")
    print("   - Client: client = FTPClient(); client.connect()")
    print("\nOtomatik test başlatılıyor...")
    test_ftp()