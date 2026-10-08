"""
Çok İstemcili UDP İstemcisi (UDP Multi-user Client)
--------------------------------------------------
Önemli Noktalar ve Açıklamalar:
1. İstemcide Neden Thread (İş Parçacığı) Kullanılır?
   - Sunucu tarafında tek döngü yeterliyken, istemci tarafında kullanıcıdan girdi alan
     `input()` fonksiyonu kodun akışını kilitler (blocking).
   - Kullanıcı klavyeden bir şey yazmasa bile diğer istemcilerden gelen mesajları
     anlık olarak ekrana basabilmek için, mesaj alma (recvfrom) işlemi ayrı bir
     iş parçacığında (arka plan thread) yürütülür.

2. Bağlantı Durumu:
   - TCP'deki gibi `connect()` zorunluluğu yoktur.
   - İstemci sunucuya ilk mesajını gönderdiği anda sunucunun aktif kullanıcı listesine eklenir.

3. Çıkış (:q):
   - Kullanıcı :q yazdığında sunucuya bildirilir ve soket kapatılarak program sonlanır.
"""
import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 65432

def receive_messages(sock):
    """
    Sunucudan gelen yayın (broadcast) mesajlarını sürekli dinleyen arka plan fonksiyonu.
    Ayrı bir thread içinde çalıştırılır.
    """
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            message = data.decode('utf-8')
            
            # Sunucu çıkışımızı onayladıysa dinleme döngüsünden çık
            if message == ':q':
                break
                
            # Gelen mesajı ekrana yazdır
            print(f"\n{message}\nSizin mesajınız: ", end="", flush=True)
        except OSError:
            # Soket kapatıldığında bu hata alınabilir; döngüyü sessizce bitir
            break
        except Exception as e:
            print(f"\n[!] Mesaj alma hatası: {e}")
            break

# UDP soketi oluşturma
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sunucuya giriş yaptığımızı bildirmek için bir ilk selamlama paketi gönderiyoruz
ilk_mesaj = "Merhaba, sohbete katıldım!"
s.sendto(ilk_mesaj.encode('utf-8'), (HOST, PORT))

# Sunucudan gelen mesajları dinleyecek arka plan iş parçacığını (thread) başlat
# daemon=True: Ana program kapandığında bu thread'in de otomatik kapanmasını sağlar
alici_thread = threading.Thread(target=receive_messages, args=(s,), daemon=True)
alici_thread.start()

print("=" * 50)
print("Sohbete bağlandınız! Mesajınızı yazıp Enter'a basınız.")
print("Çıkmak için ':q' yazabilirsiniz.")
print("=" * 50)

try:
    while True:
        mesaj = input("Sizin mesajınız: ")
        
        # Boş mesaj kontrolü
        if not mesaj.strip():
            continue
            
        # Mesajı sunucuya gönder
        s.sendto(mesaj.encode('utf-8'), (HOST, PORT))
        
        # Çıkış kontrolü
        if mesaj.lower() == ':q':
            print("Sohbetten ayrılıyorsunuz...")
            break

except KeyboardInterrupt:
    # Ctrl+C ile çıkış yapıldığında da sunucuya çıkış bildirimi gönder
    s.sendto(":q".encode('utf-8'), (HOST, PORT))
    print("\nProgram kapatılıyor...")

finally:
    s.close()
    print("İstemci sonlandı. Hoşça kalın!")
