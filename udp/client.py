"""
UDP İstemcisi (Client) vs TCP İstemcisi Farkları:
------------------------------------------------
1. Bağlantı Kurulumu (connect):
   - TCP: İletişimden önce `s.connect((HOST, PORT))` zorunludur. 3'lü el sıkışma yapılır.
          Sunucu kapalıysa istemci anında `ConnectionRefusedError` hatası verir.
   - UDP: `connect()` zorunlu DEĞİLDİR (el sıkışma yoktur). Soket oluşturulur ve
          doğrudan veri gönderilmeye başlanır. Sunucu kapalı olsa bile `sendto()` hata vermez,
          paket ağa bırakılır.

2. Veri Gönderme:
   - TCP: `s.sendall(veri)` kullanılır (hedef adres verilmez, çünkü bağlantı önceden kurulmuştur).
   - UDP: `s.sendto(veri, (HOST, PORT))` kullanılır (her pakette hedef IP ve port açıkça belirtilir).

3. Veri Alma:
   - TCP: `s.recv(1024)` sadece gelen baytları döner.
   - UDP: `s.recvfrom(1024)` hem gelen veriyi hem de gönderenin adresini `(data, server_addr)` döner.

4. Güvenilirlik & Bloklanma:
   - TCP: Karşı tarafa ulaşıp ulaşmadığı işletim sistemi tarafından doğrulanır.
   - UDP: Gönderilen paketin sunucuya ulaştığı garanti edilmez. Sunucu yanıt vermezse
          `recvfrom()` sonsuza kadar yanıt bekleyebilir (çözüm için `s.settimeout()` kullanılabilir).
"""
import socket

# Sunucunun IP adresi ve port numarası
HOST = '127.0.0.1'
PORT = 65432

# UDP soketi oluşturma (TCP'deki SOCK_STREAM yerine SOCK_DGRAM kullanılır)
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    # TCP'de burada `s.connect((HOST, PORT))` yapılması gerekirdi.
    # UDP'de bağlantı kurulmaz; soket hazır olduğunda doğrudan gönderim yapılabilir.

    # --- [OPSİYONEL] ZAMAN AŞIMI (TIMEOUT) AYARI ---
    # UDP'de bağlantı ve el sıkışma olmadığı için, sunucu kapalıysa veya gönderilen paket
    # yolda kaybolursa istemci recvfrom() satırında sonsuza kadar bloke olur (yanıt bekler).
    # Bunu engellemek için sokete bir bekleme süresi (timeout) atanabilir:
    # s.settimeout(5.0)  # 5 saniye içinde veri gelmezse socket.timeout istisnası fırlatır

    print("Mesajlaşmaya başlayabilirsiniz.")
    print(":q yazarak çıkış yapabilirsiniz.")
    
    while True:
        message = input("Sizin mesajınız: ")
        
        # Sunucuya mesajı ve sunucunun adresini gönder:
        # TCP'deki sendall() yerine her pakette hedef adresi içeren sendto() kullanılır.
        s.sendto(message.encode('utf-8'), (HOST, PORT))
        
        if message.lower() == ':q':
            break
            
        # Sunucudan yanıt bekleme:
        # TCP'deki recv() yerine yanıtı ve gönderen sunucunun adresini dönen recvfrom() kullanılır.

        # --- [TIMEOUT AÇILDIĞINDA KULLANILACAK BLOK] ---
        # Yukarıdaki `s.settimeout(5.0)` satırını açarsanız, hatayı yakalamak için
        # aşağıdaki try-except bloğunu aktif edip alttaki yalın recvfrom satırlarını yoruma alabilirsiniz:
        
        # try:
        #     data, server_addr = s.recvfrom(1024)
        #     response = data.decode('utf-8')
        #     print(f"Sunucudan gelen mesaj: {response}")
        # except socket.timeout:
        #     print("[UYARI] Sunucudan belirtilen sürede yanıt alınamadı (Zaman aşımı / Paket kaybı)!")
        #     continue

        data, server_addr = s.recvfrom(1024)
        response = data.decode('utf-8')
        print(f"Sunucudan gelen mesaj: {response}")
        
        if response.lower() == ':q':
            print("Sunucu bağlantıyı sonlandırdı.")
            break

print("İstemci programı sonlanıyor. Hoşça kalın!")