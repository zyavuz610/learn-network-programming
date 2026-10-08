"""
=============================================================================
TELNET SUNUCUSU İÇİN PYTHON İSTEMCİSİ (client.py)
=============================================================================
Bu dosya, 2_telnet-socket/server.py sunucusuna bağlanmak için kullanabileceğiniz
standart Python istemcisidir. 

Eğer sisteminizde Telnet yüklü değilse ya da doğrudan Python üzerinden 
sunucuya bağlanıp test etmek isterseniz bu istemciyi çalıştırabilirsiniz.

Kullanım:
    python client.py

Özellikler:
- Arka planda çalışan bir dinleme thread'i (receive thread) ile sunucudan 
  gelen mesajları ve Telnet promptlarını anlık ekrana yazar.
- Gönderilen her mesaja Telnet uyumluluğu için '\r\n' (CRLF) ekler.
- Çıkış için 'q', 'quit' veya 'exit' yazılabilir.
=============================================================================
"""

import socket
import threading
import sys

HOST = '127.0.0.1'  # Sunucu IP adresi
PORT = 65432        # Sunucu Port numarası

def receive_messages(client_socket):
    """
    Sunucudan gelen verileri (karşılama metni, prompt, diğer istemci mesajları)
    kesintisiz olarak dinler ve ekrana yazar.
    """
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("\n[!] Sunucu bağlantıyı kapattı.")
                break
            
            # Gelen veriyi satır sonu bozulmadan doğrudan terminale aktar
            sys.stdout.write(data.decode('utf-8', errors='ignore'))
            sys.stdout.flush()
        except Exception:
            break

def start_client():
    """İstemciyi başlatan fonksiyon."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"[!] Hata: {HOST}:{PORT} adresindeki sunucuya bağlanılamadı.")
        print("[!] Lütfen önce 'python server.py' dosyasını çalıştırdığınızdan emin olun.")
        return

    # Sunucudan gelen mesajları anlık dinleyen arka plan iş parçacığı (Daemon Thread)
    recv_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    recv_thread.daemon = True
    recv_thread.start()

    try:
        while True:
            # Kullanıcıdan mesaj al
            message = input()
            
            # Çıkış komutları
            if message.lower() in ['q', 'quit', 'exit']:
                # Sunucuya çıkış mesajını gönder ve döngüyü bitir
                client_socket.sendall((message + "\r\n").encode('utf-8'))
                break
            
            # Mesajın sonuna CRLF (\r\n) ekleyerek sunucuya ilet
            client_socket.sendall((message + "\r\n").encode('utf-8'))
            
    except KeyboardInterrupt:
        pass
    finally:
        client_socket.close()
        print("\n[*] İstemci kapatıldı.")

if __name__ == "__main__":
    start_client()
