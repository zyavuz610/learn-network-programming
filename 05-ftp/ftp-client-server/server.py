# server.py - FTP Server
import socket
import threading
import os
import time

class FTPServer:
    def __init__(self, host='localhost', port=21, root_dir='ftp_data'):
        self.host = host
        self.port = port
        self.root_dir = root_dir
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Sunucu kök dizinini ve data.txt dosyasını oluştur
        self.setup_server_directory()
    
    def setup_server_directory(self):
        """Server dizinini ve data.txt dosyasını oluşturur"""
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)
            print(f"Server dizini oluşturuldu: {self.root_dir}")
        
        # data.txt dosyasını oluştur
        data_file = os.path.join(self.root_dir, "data.txt")
        if not os.path.exists(data_file):
            with open(data_file, 'w', encoding='utf-8') as f:
                f.write("Bu FTP server üzerindeki data.txt dosyasıdır.\n")
                f.write("Bu dosya client tarafından indirilebilir.\n")
                f.write("FTP protokolü test verisidir.\n")
                f.write("Dosya boyutu: yaklaşık 150 byte\n")
                f.write("Oluşturulma tarihi: " + time.strftime("%Y-%m-%d %H:%M:%S"))
            print(f"data.txt dosyası oluşturuldu: {data_file}")
    
    def start(self):
        """FTP server'ı başlatır"""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            print(f"FTP Server başlatıldı")
            print(f"Adres: {self.host}:{self.port}")
            print(f"Kök dizin: {os.path.abspath(self.root_dir)}")
            print("İstemci bağlantıları bekleniyor...")
            print("-" * 50)
            
            while True:
                client_socket, address = self.socket.accept()
                print(f"[{time.strftime('%H:%M:%S')}] Yeni bağlantı: {address[0]}:{address[1]}")
                
                # Her istemci için ayrı thread başlat
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\nServer kapatılıyor...")
            self.socket.close()
        except Exception as e:
            print(f"Server hatası: {e}")
            self.socket.close()
    
    def handle_client(self, client_socket, address):
        """İstemci bağlantısını yönetir"""
        current_dir = self.root_dir
        client_id = f"{address[0]}:{address[1]}"
        
        try:
            # Karşılama mesajı
            self.send_response(client_socket, "220 FTP Server Hazır - data.txt dosyası mevcut")
            
            while True:
                # İstemciden komut al
                data = client_socket.recv(1024).decode('utf-8').strip()
                if not data:
                    print(f"[{client_id}] Bağlantı kesildi")
                    break
                
                print(f"[{client_id}] Komut: {data}")
                
                # Komutları işle
                if data.upper().startswith('USER'):
                    username = data.split(' ')[1] if len(data.split(' ')) > 1 else 'anonymous'
                    print(f"[{client_id}] Kullanıcı: {username}")
                    self.send_response(client_socket, "331 Kullanıcı adı tamam, şifre bekleniyor")
                
                elif data.upper().startswith('PASS'):
                    password = data.split(' ')[1] if len(data.split(' ')) > 1 else ''
                    print(f"[{client_id}] Şifre alındı")
                    self.send_response(client_socket, "230 Giriş başarılı")
                
                elif data.upper() == 'PWD':
                    rel_path = os.path.relpath(current_dir, self.root_dir)
                    display_path = '/' if rel_path == '.' else '/' + rel_path.replace('\\', '/')
                    self.send_response(client_socket, f'257 "{display_path}" mevcut dizin')
                
                elif data.upper().startswith('CWD'):
                    if len(data.split(' ')) > 1:
                        path = ' '.join(data.split(' ')[1:])
                        new_dir = os.path.join(current_dir, path)
                        new_dir = os.path.abspath(new_dir)
                        
                        # Güvenlik: root dizin dışına çıkmasını engelle
                        if new_dir.startswith(os.path.abspath(self.root_dir)) and os.path.exists(new_dir) and os.path.isdir(new_dir):
                            current_dir = new_dir
                            print(f"[{client_id}] Dizin değiştirildi: {new_dir}")
                            self.send_response(client_socket, "250 Dizin değiştirildi")
                        else:
                            self.send_response(client_socket, "550 Dizin bulunamadı veya erişim engellendi")
                    else:
                        self.send_response(client_socket, "501 Dizin adı gerekli")
                
                elif data.upper() == 'LIST':
                    file_list = self.get_directory_listing(current_dir)
                    response = "150 Dizin listesi gönderiliyor\r\n"
                    response += file_list
                    response += "226 Dizin listesi gönderildi"
                    self.send_response(client_socket, response)
                
                elif data.upper().startswith('RETR'):
                    if len(data.split(' ')) > 1:
                        filename = ' '.join(data.split(' ')[1:])
                        self.handle_download(client_socket, current_dir, filename, client_id)
                    else:
                        self.send_response(client_socket, "501 Dosya adı gerekli")
                
                elif data.upper().startswith('STOR'):
                    if len(data.split(' ')) > 1:
                        filename = ' '.join(data.split(' ')[1:])
                        self.handle_upload(client_socket, current_dir, filename, client_id)
                    else:
                        self.send_response(client_socket, "501 Dosya adı gerekli")
                
                elif data.upper() == 'QUIT':
                    print(f"[{client_id}] Çıkış yapıyor")
                    self.send_response(client_socket, "221 Güle güle!")
                    break
                
                elif data.upper() == 'HELP':
                    help_text = """214-Desteklenen komutlar:
USER - Kullanıcı adı
PASS - Şifre
PWD  - Mevcut dizin
CWD  - Dizin değiştir
LIST - Dosya listesi
RETR - Dosya indir
STOR - Dosya yükle
QUIT - Çıkış
HELP - Yardım
214 Yardım sonu"""
                    self.send_response(client_socket, help_text)
                
                else:
                    self.send_response(client_socket, f"502 '{data}' komutu desteklenmiyor")
        
        except Exception as e:
            print(f"[{client_id}] İstemci hatası: {e}")
        finally:
            client_socket.close()
            print(f"[{client_id}] Bağlantı kapatıldı")
    
    def send_response(self, client_socket, message):
        """İstemciye yanıt gönderir"""
        try:
            if not message.endswith('\r\n'):
                message += '\r\n'
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Yanıt gönderme hatası: {e}")
    
    def get_directory_listing(self, directory):
        """Dizin içeriğini listeler"""
        file_list = ""
        try:
            items = sorted(os.listdir(directory))
            for item in items:
                item_path = os.path.join(directory, item)
                stat_info = os.stat(item_path)
                mod_time = time.strftime("%b %d %H:%M", time.localtime(stat_info.st_mtime))
                
                if os.path.isdir(item_path):
                    file_list += f"drwxr-xr-x 2 user user 4096 {mod_time} {item}\r\n"
                else:
                    size = stat_info.st_size
                    file_list += f"-rw-r--r-- 1 user user {size:>8} {mod_time} {item}\r\n"
        except Exception as e:
            file_list = f"Dizin okuma hatası: {str(e)}\r\n"
        
        return file_list
    
    def handle_download(self, client_socket, current_dir, filename, client_id):
        """Dosya indirme işlemini yönetir"""
        filepath = os.path.join(current_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"[{client_id}] Dosya bulunamadı: {filename}")
            self.send_response(client_socket, "550 Dosya bulunamadı")
            return
        
        if not os.path.isfile(filepath):
            print(f"[{client_id}] Bu bir dosya değil: {filename}")
            self.send_response(client_socket, "550 Bu bir dosya değil")
            return
        
        try:
            file_size = os.path.getsize(filepath)
            print(f"[{client_id}] Dosya indiriliyor: {filename} ({file_size} byte)")
            
            # Dosya gönderme başlangıcını bildir
            self.send_response(client_socket, "150 Dosya gönderiliyor")
            
            # Dosyayı oku ve gönder
            with open(filepath, 'rb') as file:
                # Önce dosya boyutunu gönder
                size_header = f"SIZE:{file_size}:"
                client_socket.send(size_header.encode('utf-8'))
                
                # Dosya içeriğini chunks halinde gönder
                bytes_sent = 0
                while True:
                    chunk = file.read(4096)
                    if not chunk:
                        break
                    client_socket.send(chunk)
                    bytes_sent += len(chunk)
                
                # Dosya sonu işaretçisi
                client_socket.send(b"\r\nEOF\r\n")
            
            print(f"[{client_id}] Dosya gönderildi: {filename} ({bytes_sent} byte)")
            self.send_response(client_socket, "226 Dosya başarıyla gönderildi")
            
        except Exception as e:
            print(f"[{client_id}] Dosya gönderme hatası: {e}")
            self.send_response(client_socket, f"550 Dosya gönderme hatası: {str(e)}")
    
    def handle_upload(self, client_socket, current_dir, filename, client_id):
        """Dosya yükleme işlemini yönetir"""
        filepath = os.path.join(current_dir, filename)
        
        try:
            print(f"[{client_id}] Dosya yükleniyor: {filename}")
            self.send_response(client_socket, "150 Dosya yükleme hazır")
            
            # Dosya verisini al
            file_data = b""
            while True:
                chunk = client_socket.recv(4096)
                if chunk.endswith(b"\r\nEOF\r\n"):
                    file_data += chunk[:-7]  # EOF işaretçisini çıkar
                    break
                file_data += chunk
            
            # Dosyayı kaydet
            with open(filepath, 'wb') as file:
                file.write(file_data)
            
            file_size = len(file_data)
            print(f"[{client_id}] Dosya kaydedildi: {filename} ({file_size} byte)")
            self.send_response(client_socket, "226 Dosya başarıyla yüklendi")
            
        except Exception as e:
            print(f"[{client_id}] Dosya yükleme hatası: {e}")
            self.send_response(client_socket, f"550 Dosya yükleme hatası: {str(e)}")


def main():
    """Ana fonksiyon"""
    print("=" * 60)
    print("FTP SERVER - server.py")
    print("=" * 60)
    
    # Server ayarları
    HOST = 'localhost'
    PORT = 2121  # Standart FTP port 21 yerine 2121 kullan (yetki problemi için)
    
    try:
        # Server oluştur ve başlat
        server = FTPServer(HOST, PORT)
        server.start()
        
    except KeyboardInterrupt:
        print("\nServer kapatılıyor...")
    except Exception as e:
        print(f"Server başlatma hatası: {e}")
        print("Not: Port 21 kullanımı için admin yetkisi gerekebilir.")
        print("Alternatif olarak farklı bir port deneyin (örn: 2121)")


if __name__ == "__main__":
    main()