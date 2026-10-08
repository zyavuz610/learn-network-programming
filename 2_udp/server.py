"""
UDP (User Datagram Protocol) vs TCP (Transmission Control Protocol) Farkları:
-------------------------------------------------------------------------
1. Bağlantı Yapısı:
   - TCP: Bağlantı odaklıdır (Connection-oriented). Veri göndermeden önce 3'lü el sıkışma
          (3-way handshake) ile bağlantı kurulur (connect(), listen(), accept()).
   - UDP: Bağlantısızdır (Connectionless). Önceden el sıkışma veya oturum açma yoktur;
          paketler doğrudan hedefe gönderilir.

2. Güvenilirlik ve Sıralama:
   - TCP: Güvenilirdir (Reliable). Paket ulaştı mı kontrol edilir (ACK). Kaybolan paket
          tekrar gönderilir ve paketlerin doğru sırada gitmesi garanti edilir.
   - UDP: Garantisizdir (Best-effort). Paket kaybı kontrol edilmez, kaybolan paket tekrar
          gönderilmez, paketlerin gidiş sırası garanti edilmez.

3. Hız ve Başlık (Header) Boyutu:
   - TCP: Ek kontrol mekanizmaları nedeniyle gecikme daha fazladır; başlık min. 20 byte'tır.
   - UDP: Kontrol mekanizması olmadığı için çok hızlıdır ve düşük gecikmelidir; başlık sabittir (8 byte).

4. Veri İletim Tipi ve Fonksiyonlar:
   - TCP: Bayt akışı (Stream - SOCK_STREAM). recv() ve sendall() kullanılır.
   - UDP: Bağımsız paketler (Datagram - SOCK_DGRAM). Her pakette hedef/kaynak adresi yer alır,
          bu yüzden recvfrom() ve sendto() kullanılır.

5. Kullanım Alanları:
   - TCP: Web (HTTP/HTTPS), dosya transferi (FTP), e-posta (SMTP), SSH.
   - UDP: Canlı yayın / ses iletişimi (VoIP), çevrim içi oyunlar, DNS sorguları.
"""
import socket

# Sunucunun IP adresi ve port numarası
HOST = '127.0.0.1'
PORT = 65432

# UDP soketi oluşturma (TCP'deki SOCK_STREAM yerine SOCK_DGRAM kullanılır)
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    # TCP'de gereken s.listen() ve s.accept() adımları UDP'de bağlantı kurulmadığı için yoktur.
    print(f"Sunucu {HOST}:{PORT} adresinde dinliyor...")
    
    while True:
        # İstemciden mesaj ve adresi al (TCP'deki conn.recv() yerine recvfrom() kullanılır;
        # çünkü bağlantı olmadığından mesajın kimden (addr) geldiği de öğrenilmelidir)
        data, addr = s.recvfrom(1024)
        message = data.decode('utf-8')
        
        print(f"İstemci {addr} adresinden gelen mesaj: {message}")
        
        if message.lower() == ':q':
            print("İstemci bağlantıyı sonlandırdı.")
            break
        
        # Sunucudan istemciye yanıt gönderme (TCP'deki conn.sendall() yerine sendto() kullanılır;
        # her paket için alıcı adresi açıkça verilir)
        response = input("Sizin mesajınız: ")
        s.sendto(response.encode('utf-8'), addr)
        
        if response.lower() == ':q':
            print("Sunucu bağlantıyı sonlandırdı.")
            break

print("Sunucu programı sonlanıyor. Hoşça kalın!")