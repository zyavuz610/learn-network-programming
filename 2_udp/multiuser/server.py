"""
Çok İstemcili UDP Sunucusu (UDP Multi-user Broadcast / Chat Server)
-----------------------------------------------------------------
Önemli Noktalar ve TCP ile Karşılaştırma:
1. Thread (İş Parçacığı) İhtiyacı Yoktur:
   - TCP'de (örn. threaded_server.py) her istemci için ayrı bir thread (iş parçacığı)
     ve thread güvenliği için kilitler (threading.Lock) açmak zorundaydık.
   - UDP'de bağlantı (connection) kavramı olmadığı için sunucu tek bir soket ve
     tek bir while döngüsü ile yüzlerce istemciyi eşzamanlı olarak yönetebilir.

2. İstemcilerin Yönetimi:
   - Sunucu, mesaj gönderen istemcilerin adreslerini (IP, Port) bir kümede (set) tutar.
   - Gelen her mesaj, paketi gönderen hariç diğer tüm kayıtlı istemcilere s.sendto() ile iletilir (Broadcast / Relay).

3. Bağlantısızlık:
   - İstemcilerin sunucuya 'bağlanması' için bir el sıkışma gerekmez; ilk mesajlarını attıkları anda
     adresleri listeye kaydedilmiş olur.
"""
import socket

HOST = '127.0.0.1'
PORT = 65432

# Aktif istemcilerin adreslerini (IP, PORT) saklayacağımız küme
# Not: UDP tek thread üzerinden çalıştığı için burada race-condition veya Lock ihtiyacı yoktur!
clients = set()

# UDP Soketi oluşturma (SOCK_DGRAM)
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"[*] Çok istemcili UDP Sunucusu {HOST}:{PORT} adresinde dinliyor...")
    print("[*] Gelen mesajlar diğer tüm istemcilere iletilecektir.\n")

    while True:
        try:
            # Herhangi bir istemciden paket bekle
            data, addr = s.recvfrom(1024)
            message = data.decode('utf-8').strip()

            # Yeni bir istemci mi geldi?
            if addr not in clients:
                clients.add(addr)
                print(f"[+] Yeni istemci katıldı: {addr} (Toplam aktif istemci: {len(clients)})")
                # Diğer istemcilere katılım bilgisini duyur
                katilim_mesaji = f"--- [SİSTEM] {addr} sohbete katıldı ---"
                for client_addr in clients:
                    if client_addr != addr:
                        s.sendto(katilim_mesaji.encode('utf-8'), client_addr)

            # İstemci ayrılmak mı istiyor?
            if message.lower() == ':q':
                clients.remove(addr)
                print(f"[-] İstemci ayrıldı: {addr} (Kalan istemci: {len(clients)})")
                
                # Ayrılan istemciye onay gönder
                s.sendto(":q".encode('utf-8'), addr)
                
                # Diğer istemcilere ayrılma bilgisini duyur
                ayrilma_mesaji = f"--- [SİSTEM] {addr} sohbetten ayrıldı ---"
                for client_addr in clients:
                    s.sendto(ayrilma_mesaji.encode('utf-8'), client_addr)
                continue

            # Normal sohbet mesajı: Göndereni ekrana yaz
            print(f"[{addr}]: {message}")

            # Mesajı gönderen hariç diğer tüm istemcilere ilet (Broadcast)
            broadcast_mesaji = f"[{addr}]: {message}"
            for client_addr in clients:
                if client_addr != addr:
                    try:
                        s.sendto(broadcast_mesaji.encode('utf-8'), client_addr)
                    except Exception as e:
                        print(f"[!] {client_addr} adresine gönderim hatası: {e}")

        except KeyboardInterrupt:
            print("\n[*] Sunucu kullanıcı tarafından kapatılıyor...")
            break
        except Exception as e:
            print(f"[!] Hata meydana geldi: {e}")

print("[*] Sunucu kapatıldı.")
