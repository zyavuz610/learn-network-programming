# client.py - FTP Client
import socket
import os
import time

class FTPClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.logged_in = False
    
    def connect(self, host='localhost', port=2121):
        """FTP server'a bağlanır"""
        try:
            print(f"Sunucuya bağlanılıyor: {host}:{port}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            
            # Server'dan karşılama mesajını al
            response = self.receive_response()
            print(f"Server: {response}")
            
            if response.startswith('220'):
                self.connected = True
                print("✓ Sunucuya başarıyla bağlandı!")
                return True
            else:
                print("✗ Server bağlantısı başarısız!")
                return False
                
        except ConnectionRefusedError:
            print("✗ Sunucuya bağlanılamadı! Server çalışıyor mu?")
            return False
        except Exception as e:
            print(f"✗ Bağlantı hatası: {e}")
            return False
    
    def login(self, username="user", password="pass"):
        """FTP server'a giriş yapar"""
        if not self.connected:
            print("✗ Önce sunucuya bağlanmalısınız!")
            return False
        
        try:
            # Kullanıcı adını gönder
            print(f"Kullanıcı adı gönderiliyor: {username}")
            self.send_command(f"USER {username}")
            response = self.receive_response()
            print(f"Server: {response}")
            
            if not response.startswith('331'):
                print("✗ Kullanıcı adı reddedildi!")
                return False
            
            # Şifreyi gönder
            print("Şifre gönderiliyor...")
            self.send_command(f"PASS {password}")
            response = self.receive_response()
            print(f"Server: {response}")
            
            if response.startswith('230'):
                self.logged_in = True
                print("✓ Giriş başarılı!")
                return True
            else:
                print("✗ Şifre reddedildi!")
                return False
                
        except Exception as e:
            print(f"✗ Giriş hatası: {e}")
            return False
    
    def pwd(self):
        """Mevcut dizini gösterir"""
        if not self.check_connection():
            return None
        
        try:
            self.send_command("PWD")
            response = self.receive_response()
            print(f"Mevcut dizin: {response}")
            return response
        except Exception as e:
            print(f"✗ Dizin bilgisi alınamadı: {e}")
            return None
    
    def list_files(self):
        """Server'daki dosyaları listeler"""
        if not self.check_connection():
            return False
        
        try:
            print("Dosya listesi alınıyor...")
            self.send_command("LIST")
            response = self.receive_response()
            
            # Çok satırlı yanıtı işle
            lines = response.split('\r\n')
            print("\n" + "="*60)
            print("SERVER DİZİN İÇERİĞİ:")
            print("="*60)
            
            for line in lines:
                if line and not line.startswith('150') and not line.startswith('226'):
                    print(line)
            
            print("="*60)
            return True
            
        except Exception as e:
            print(f"✗ Dosya listesi alınamadı: {e}")
            return False
    
    def download_file(self, remote_filename, local_filename=None):
        """Server'dan dosya indirir"""
        if not self.check_connection():
            return False
        
        if local_filename is None:
            local_filename = remote_filename
        
        try:
            print(f"\nDosya indiriliyor: {remote_filename}")
            print(f"Kaydedilecek yer: {local_filename}")
            
            # RETR komutunu gönder
            self.send_command(f"RETR {remote_filename}")
            response = self.receive_response()
            print(f"Server yanıtı: {response}")
            
            if not response.startswith('150'):
                print(f"✗ Dosya indirilemedi: {response}")
                return False
            
            # Dosya boyut bilgisini al
            size_data = b""
            while True:
                chunk = self.socket.recv(1)
                size_data += chunk
                if size_data.endswith(b":"):
                    break
            
            # Boyut bilgisini çöz
            size_info = size_data.decode('utf-8')
            if size_info.startswith("SIZE:"):
                file_size = int(size_info.split(':')[1])
                print(f"Dosya boyutu: {file_size} byte")
            else:
                print("Boyut bilgisi alınamadı")
                file_size = 0
            
            # Dosya verisini al
            print("Dosya verisi indiriliyor...")
            file_data = b""
            total_received = 0
            
            while True:
                chunk = self.socket.recv(4096)
                if chunk.endswith(b"\r\nEOF\r\n"):
                    file_data += chunk[:-7]  # EOF işaretçisini çıkar
                    total_received += len(chunk) - 7
                    break
                file_data += chunk
                total_received += len(chunk)
                
                # İlerleme göster
                if file_size > 0:
                    progress = (total_received / file_size) * 100
                    print(f"\rİlerleme: %{progress:.1f} ({total_received}/{file_size} byte)", end="", flush=True)
            
            print()  # Yeni satır
            
            # Dosyayı kaydet
            with open(local_filename, 'wb') as f:
                f.write(file_data)
            
            # Son server yanıtını al
            final_response = self.receive_response()
            print(f"Server: {final_response}")
            
            # Dosya bilgilerini göster
            actual_size = len(file_data)
            print(f"✓ Dosya başarıyla indirildi!")
            print(f"  Dosya adı: {local_filename}")
            print(f"  Boyut: {actual_size} byte")
            print(f"  Konum: {os.path.abspath(local_filename)}")
            
            # Dosya içeriğini göster (metin dosyası ise)
            try:
                with open(local_filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                if len(content) < 500:  # Küçük dosyalar için içeriği göster
                    print(f"\nDOSYA İÇERİĞİ:")
                    print("-" * 40)
                    print(content)
                    print("-" * 40)
            except:
                pass  # Binary dosya veya okuma hatası
            
            return True
            
        except Exception as e:
            print(f"\n✗ Dosya indirme hatası: {e}")
            return False
    
    def upload_file(self, local_filename, remote_filename=None):
        """Server'a dosya yükler"""
        if not self.check_connection():
            return False
        
        if remote_filename is None:
            remote_filename = os.path.basename(local_filename)
        
        if not os.path.exists(local_filename):
            print(f"✗ Dosya bulunamadı: {local_filename}")
            return False
        
        try:
            file_size = os.path.getsize(local_filename)
            print(f"\nDosya yükleniyor: {local_filename}")
            print(f"Server'daki adı: {remote_filename}")
            print(f"Boyut: {file_size} byte")
            
            # STOR komutunu gönder
            self.send_command(f"STOR {remote_filename}")
            response = self.receive_response()
            print(f"Server yanıtı: {response}")
            
            if not response.startswith('150'):
                print(f"✗ Dosya yüklenemedi: {response}")
                return False
            
            # Dosyayı oku ve gönder
            print("Dosya gönderiliyor...")
            with open(local_filename, 'rb') as f:
                bytes_sent = 0
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    self.socket.send(chunk)
                    bytes_sent += len(chunk)
                    
                    # İlerleme göster
                    progress = (bytes_sent / file_size) * 100
                    print(f"\rİlerleme: %{progress:.1f} ({bytes_sent}/{file_size} byte)", end="", flush=True)
            
            # Dosya sonu işaretçisi gönder
            self.socket.send(b"\r\nEOF\r\n")
            
            print()  # Yeni satır
            
            # Server yanıtını al
            final_response = self.receive_response()
            print(f"Server: {final_response}")
            
            if final_response.startswith('226'):
                print(f"✓ Dosya başarıyla yüklendi: {remote_filename}")
                return True
            else:
                print(f"✗ Dosya yükleme başarısız: {final_response}")
                return False
            
        except Exception as e:
            print(f"\n✗ Dosya yükleme hatası: {e}")
            return False
    
    def change_directory(self, directory):
        """Dizin değiştirir"""
        if not self.check_connection():
            return False
        
        try:
            self.send_command(f"CWD {directory}")
            response = self.receive_response()
            print(f"Server: {response}")
            return response.startswith('250')
        except Exception as e:
            print(f"✗ Dizin değiştirilemedi: {e}")
            return False
    
    def help_command(self):
        """Server'dan yardım bilgisi alır"""
        if not self.check_connection():
            return False
        
        try:
            self.send_command("HELP")
            response = self.receive_response()
            print("Server yardım bilgisi:")
            print("-" * 40)
            for line in response.split('\r\n'):
                if line:
                    print(line)
            print("-" * 40)
            return True
        except Exception as e:
            print(f"✗ Yardım bilgisi alınamadı: {e}")
            return False
    
    def quit(self):
        """FTP bağlantısını sonlandırır"""
        if self.connected:
            try:
                self.send_command("QUIT")
                response = self.receive_response()
                print(f"Server: {response}")
            except:
                pass
            
            self.socket.close()
            self.connected = False
            self.logged_in = False
            print("✓ Bağlantı sonlandırıldı")
    
    def send_command(self, command):
        """Server'a komut gönderir"""
        if not command.endswith('\r\n'):
            command += '\r\n'
        self.socket.send(command.encode('utf-8'))
    
    def receive_response(self):
        """Server'dan yanıt alır"""
        response = ""
        while True:
            chunk = self.socket.recv(4096).decode('utf-8')
            response += chunk
            if '\r\n' in response:
                break
        return response.strip()
    
    def check_connection(self):
        """Bağlantı durumunu kontrol eder"""
        if not self.connected:
            print("✗ Sunucuya bağlı değilsiniz!")
            return False
        if not self.logged_in:
            print("✗ Önce giriş yapmalısınız!")
            return False
        return True


def interactive_menu(client):
    """İnteraktif menü"""
    while True:
        print("\n" + "="*50)
        print("FTP CLIENT MENÜ")
        print("="*50)
        print("1. Dosya Listesi (LIST)")
        print("2. data.txt İndir (RETR)")
        print("3. Dosya Yükle (STOR)")
        print("4. Mevcut Dizin (PWD)")
        print("5. Dizin Değiştir (CWD)")
        print("6. Yardım (HELP)")
        print("7. Çıkış (QUIT)")
        print("-"*50)
        
        choice = input("Seçiminiz (1-7): ").strip()
        
        if choice == '1':
            client.list_files()
        
        elif choice == '2':
            print("\n--- data.txt DOSYASI İNDİRİLİYOR ---")
            success = client.download_file("data.txt", "downloaded_data.txt")
            if success:
                print("✓ data.txt başarıyla indirildi -> downloaded_data.txt")
            else:
                print("✗ data.txt indirilemedi!")
        
        elif choice == '3':
            filename = input("Yüklenecek dosya adı: ").strip()
            if filename and os.path.exists(filename):
                remote_name = input(f"Server'daki adı ({os.path.basename(filename)}): ").strip()
                if not remote_name:
                    remote_name = os.path.basename(filename)
                client.upload_file(filename, remote_name)
            else:
                print("✗ Dosya bulunamadı!")
        
        elif choice == '4':
            client.pwd()
        
        elif choice == '5':
            directory = input("Dizin adı: ").strip()
            if directory:
                client.change_directory(directory)
        
        elif choice == '6':
            client.help_command()
        
        elif choice == '7':
            print("Çıkış yapılıyor...")
            client.quit()
            break
        
        else:
            print("✗ Geçersiz seçim!")


def auto_download_data_txt(client):
    """Otomatik data.txt indirme"""
    print("\n" + "="*60)
    print("OTOMATİK data.txt İNDİRME")
    print("="*60)
    
    # Dosya listesini göster
    print("\n1. Sunucudaki dosyalar:")
    client.list_files()
    
    # data.txt'yi indir
    print("\n2. data.txt dosyası indiriliyor...")
    success = client.download_file("data.txt", "downloaded_data.txt")
    
    if success:
        print("\n✓ OTOMATİK İNDİRME BAŞARILI!")
        print("data.txt -> downloaded_data.txt olarak kaydedildi")
    else:
        print("\n✗ Otomatik indirme başarısız!")
    
    return success


def main():
    """Ana fonksiyon"""
    print("=" * 60)
    print("FTP CLIENT - client.py")
    print("=" * 60)
    
    # Client oluştur
    client = FTPClient()
    
    # Sunucu bilgileri
    HOST = 'localhost'
    PORT = 2121
    USERNAME = 'user'
    PASSWORD = 'pass'
    
    try:
        # Sunucuya bağlan
        if not client.connect(HOST, PORT):
            print("Program sonlandırılıyor...")
            return
        
        # Giriş yap
        if not client.login(USERNAME, PASSWORD):
            print("Program sonlandırılıyor...")
            return
        
        # Kullanıcıya seçenek sun
        print("\n" + "="*50)
        print("Ne yapmak istiyorsunuz?")
        print("1. Otomatik data.txt indirme")
        print("2. İnteraktif menü")
        print("="*50)
        
        while True:
            choice = input("\nSeçiminiz (1-2): ").strip()
            
            if choice == '1':
                # Otomatik data.txt indirme
                auto_download_data_txt(client)
                break
            
            elif choice == '2':
                # İnteraktif menü
                interactive_menu(client)
                break
            
            else:
                print("✗ Geçerli seçim yapın (1 veya 2)")
    
    except KeyboardInterrupt:
        print("\n\nProgram kullanıcı tarafından sonlandırıldı")
    
    except Exception as e:
        print(f"\nBeklenmeyen hata: {e}")
    
    finally:
        # Bağlantıyı kapat
        if client.connected:
            client.quit()
        print("Program sonlandı.")


if __name__ == "__main__":
    main()