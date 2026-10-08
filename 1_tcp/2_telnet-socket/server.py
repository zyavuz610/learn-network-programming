"""
=============================================================================
TELNET UYUMLU TCP SOKET SUNUCUSU (server.py)
=============================================================================
Bu sunucu, standart Python soket programlama yapısını kullanır ve hem 
işletim sisteminin dahili TELNET istemcisiyle hem de yazılan Python 
istemcisiyle (client.py) %100 uyumlu çalışır.

-----------------------------------------------------------------------------
TELNET İLE NASIL BAĞLANILIR?
-----------------------------------------------------------------------------
1. Windows'ta Telnet İstemcisini Etkinleştirme (Varsayılan olarak kapalıdır):
   - Başlat menüsüne "Windows özelliklerini aç veya kapat" yazın.
   - Listeden "Telnet İstemcisi" (Telnet Client) seçeneğini işaretleyip "Tamam"a basın.
   - VEYA Yönetici olarak açılmış PowerShell / CMD terminalinde şu komutu çalıştırın:
     dism /online /Enable-Feature /FeatureName:TelnetClient

2. Telnet ile Sunucuya Bağlanma:
   - Önce bu sunucuyu çalıştırın:
     python server.py
   - Ayrı bir CMD, PowerShell veya Terminal penceresi açın ve şu komutu yazın:
     telnet 127.0.0.1 65432
   
   (İpucu: Eğer sisteminizde Telnet yerine Ncat/Netcat yüklüyse: ncat 127.0.0.1 65432
    ya da PuTTY kullanıyorsanız 'Raw' veya 'Telnet' modunda 127.0.0.1:65432'ye bağlanabilirsiniz.)

3. Telnet Oturumunu Sonlandırma:
   - Terminalde 'q' veya 'quit' yazıp Enter'a basabilirsiniz.
   - Ya da Telnet komut istemine geçmek için "Ctrl + ]" tuşlarına basıp ardından "quit" yazabilirsiniz.

-----------------------------------------------------------------------------
TELNET UYUMLULUĞU İÇİN NEDEN ÖZEL AYAR GEREKİR?
-----------------------------------------------------------------------------
- Satır Sonu Biçimi (CRLF): Telnet protokolünde Enter tuşu '\r\n' (Carriage Return + Line Feed)
  karakterlerini gönderir. Bu yüzden gelen veriyi işlerken '.strip()' kullanılır ve geri 
  gönderilen her metnin sonuna '\r\n' eklenir (böylece Telnet terminalinde imleç bir sonraki 
  satırın en başına düzgünce kayar).
=============================================================================
"""

import socket
import threading

HOST = '127.0.0.1'  # Sunucunun dinleyeceği adres (localhost)
PORT = 65432        # Sunucunun dinleyeceği port numarası

# Bağlı olan tüm istemci soketlerini tutan liste
clients = []

def broadcast(message, sender_socket):
    """
    Gönderen istemci haricindeki diğer tüm bağlı istemcilere mesajı yayınlar.
    """
    for client in clients[:]:
        if client != sender_socket:
            try:
                # Telnet istemcileri için satır sonuna \r\n eklenir
                client.sendall((message + "\r\n").encode('utf-8'))
            except Exception:
                client.close()
                if client in clients:
                    clients.remove(client)

def handle_client(client_socket, client_address):
    """
    Bağlanan her bir istemciyi (Telnet veya Python client) ayrı bir thread
    içinde yöneten fonksiyon.
    """
    print(f"[+] Yeni bağlantı sağlandı: {client_address}")
    
    # Telnet ile bağlanan kullanıcıya hoş geldin mesajı ve kullanım talimatı gönder
    welcome_message = (
        "\r\n"
        "====================================================\r\n"
        "  TELNET SUNUCUSUNA HOS GELDINIZ!\r\n"
        "  Cikis yapmak icin 'q' veya 'quit' yazabilirsiniz.\r\n"
        "====================================================\r\n"
        "> "
    )
    try:
        client_socket.sendall(welcome_message.encode('utf-8'))
    except Exception:
        client_socket.close()
        return

    while True:
        try:
            # İstemciden veri bekle
            data = client_socket.recv(1024)
            if not data:
                # Bağlantı koptuysa döngüden çık
                break
                
            # Gelen baytları metne çevir ve Telnet'in eklediği \r\n karakterlerini temizle
            message = data.decode('utf-8', errors='ignore').strip()
            
            # Eğer kullanıcı sadece Enter'a bastıysa boş mesaj yerine tekrar komut satırı (> ) ver
            if not message:
                client_socket.sendall(b"> ")
                continue
                
            # Çıkış komutları kontrolü
            if message.lower() in ['q', 'quit', 'exit']:
                client_socket.sendall("Gorusmek uzere, baglanti kapatiliyor...\r\n".encode('utf-8'))
                break
                
            print(f"[{client_address[0]}:{client_address[1]}]: {message}")
            
            # 1) Mesajı gönderen istemciye onay (Echo) ve yeni prompt (> ) gönder
            reply = f"Sunucu aldi: {message}\r\n> "
            client_socket.sendall(reply.encode('utf-8'))
            
            # 2) Mesajı diğer bağlı kullanıcılara da ilet (Sohbet/Broadcast ortamı)
            broadcast(f"[{client_address[1]}]: {message}", client_socket)
            
        except Exception as e:
            print(f"[!] Hata oluştu ({client_address}): {e}")
            break

    # İstemci ayrıldığında temizlik yap
    print(f"[-] Bağlantı kesildi: {client_address}")
    if client_socket in clients:
        clients.remove(client_socket)
    client_socket.close()

def start_server():
    """Sunucuyu başlatan ana dinleme fonksiyonu."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Sunucu durdurulup yeniden başlatıldığında portun hemen kullanılabilmesi için ayar
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[*] Telnet uyumlu sunucu {HOST}:{PORT} üzerinde dinliyor...")
    print(f"[*] Bağlanmak için başka bir terminalde çalıştırın: telnet {HOST} {PORT}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            clients.append(client_socket)
            
            # Her yeni bağlantı için yeni bir iş parçacığı (Thread) oluştur
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n[!] Sunucu kapatılıyor...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
