"""
Genel Çözümleyici DNS Sunucusu (Recursive / Google DNS Benzeri Sunucu)
=====================================================================

Bu program, tıpkı Google DNS (8.8.8.8) veya Cloudflare (1.1.1.1) gibi davranan modüler bir DNS sunucusudur.

ÇALIŞMA MANTIĞI (Google DNS Gibi Nasıl Çalışır?):
------------------------------------------------
1. Dinleme:
   Sunucu UDP soketi üzerinden istemcilerden gelen standart DNS sorgularını dinler.

2. Üç Aşamalı Alan Adı Çözümleme:
   İstemci bir alan adı sorduğunda (Örn: 'google.com', 'ktu.edu.tr'):
   a) Adım 1 - Sunucunun Kendi Kayıt Listesi (DNS_RECORDS):
      Sunucu önce kendi tanımlı listesine bakar. 'google.com', 'ktu.edu.tr',
      'github.com', 'ders.local' gibi popüler ve yerel alan adları doğrudan bu listeden yanıtlanır.
   b) Adım 2 - Önbellek (DNS Cache):
      Listede olmayan ama daha önce internetten çözülmüş bir ad sorulursa,
      internete tekrar çıkmadan doğrudan hafızadan (Cache HIT) çok hızlı yanıt verir.
   c) Adım 3 - İnternetten Çözümleme (Recursive Resolution):
      Kayıt ne listede ne de önbellekte varsa, sunucu internetteki gerçek DNS
      hiyerarşisine danışarak (socket.gethostbyname) IP adresini öğrenir, önbelleğe
      kaydeder ve istemciye döner.
   d) Alan adı dünyada hiç yoksa standart NXDOMAIN (Kayıt Yok) hatası döner.

NASIL KULLANILIR?
-----------------
1. Bu sunucuyu terminalden başlatın:
     python 3_dns/3_generic_dns/server.py

2. İstemci ile test edin (2 farklı yöntemle test edilebilir):

   YÖNTEM A (Python İstemcisi ile):
     Ayrı bir terminal açıp '3_dns/2_multiuser/client.py' dosyasını çalıştırın.
     İstediğiniz alan adını girin (Örn: ktu.edu.tr, wikipedia.org, ders.local).

   YÖNTEM B (Windows / Linux 'nslookup' Komutu ile):
     Terminalden doğrudan şu komutu çalıştırın:
     nslookup -port=5353 google.com 127.0.0.1
     nslookup -port=5353 ders.local 127.0.0.1
"""
import socket

# Sunucunun IP adresi ve port numarası
# Not: Standart DNS portu 53'tür; ancak yerel testlerde çakışmaları ve yönetici
# izni gereksinimini önlemek için 5353 portu kullanılmıştır.
HOST = '127.0.0.1'
PORT = 5353

# 1. Sunucunun Kendi DNS Kayıtları Listesi (Zone Veritabanı)
# google.com, ktu.edu.tr gibi popüler alan adları ve yerel alan adları doğrudan bu listeden gönderilir.
DNS_RECORDS = {
    'google.com': '142.250.185.206',
    'www.google.com': '142.250.185.206',
    'github.com': '140.82.121.4',
    'ktu.edu.tr': '193.140.70.197',
    'www.ktu.edu.tr': '193.140.70.197',
    'youtube.com': '142.250.185.174',
    'wikipedia.org': '208.80.154.224',
    'python.org': '138.197.63.241',
    'stackoverflow.com': '151.101.65.69',
    'openai.com': '13.107.246.72',
    'microsoft.com': '20.112.52.29',
    'amazon.com': '205.251.242.103',
    'ders.local': '10.0.0.1',
    'okul.yerel': '192.168.1.50',
    'proje.test': '127.0.0.1',
}

# 2. DNS Önbelleği (Cache): Listede olmayan ve internetten çözülen alan adları burada saklanır
# Format: { 'alan_adi': 'ip_adresi' }
dns_cache = {}


def parse_dns_question(data):
    """
    İstemciden gelen ikili (binary) DNS paketindeki sorgulanan alan adını okur.
    Format: \x06google\x03com\x00 -> 'google.com'
    """
    question_start = 12  # İlk 12 bayt DNS Header'dır
    parts = []
    idx = question_start

    # 0 baytını görene kadar etiketleri (label) oku
    while idx < len(data) and data[idx] != 0:
        length = data[idx]
        parts.append(data[idx + 1 : idx + 1 + length].decode('ascii', errors='ignore'))
        idx += length + 1

    return ".".join(parts).lower()


def create_dns_response(packet, ip_address=None):
    """
    İstemcinin sorgu paketine uygun RFC 1035 standartlarında bir yanıt paketi üretir.
    """
    # 1. Başlık (Header - 12 Bayt)
    transaction_id = packet[:2]  # İstemcinin Transaction ID'si aynen korunur

    if ip_address:
        flags = b'\x81\x80'   # NoError (Başarılı, QR=1, AA=1, RD=1, RA=1)
        ancount = b'\x00\x01' # 1 adet cevap
    else:
        flags = b'\x81\x83'   # NXDOMAIN (Kayıt bulunamadı)
        ancount = b'\x00\x00' # 0 cevap

    qdcount = packet[4:6]  # Soru sayısı (1)
    nscount = b'\x00\x00'
    arcount = b'\x00\x00'

    header = transaction_id + flags + qdcount + ancount + nscount + arcount

    # 2. Soru Bölümü (Question Section): Gelen paketteki soru bölümünü aynen kopyala
    null_idx = packet.find(b'\x00', 12)
    if null_idx == -1:
        return None
    question_section = packet[12 : null_idx + 5]

    # Eğer IP bulunamadıysa sadece Header + Question döner
    if not ip_address:
        return header + question_section

    # 3. Cevap Bölümü (Answer Section - A Kaydı)
    name_pointer = b'\xc0\x0c'  # Sorudaki alan adına işaret eden sıkıştırma pointer'ı
    rtype = b'\x00\x01'         # A Kaydı (IPv4)
    rclass = b'\x00\x01'        # IN (Internet Sınıfı)
    ttl = b'\x00\x00\x00\x3c'   # 60 saniye yaşam süresi (TTL)
    rdlength = b'\x00\x04'      # 4 baytlık IPv4 verisi
    rdata = socket.inet_aton(ip_address)

    answer = name_pointer + rtype + rclass + ttl + rdlength + rdata
    return header + question_section + answer


def resolve_domain(domain_name):
    """
    DNS Çözümleme Mantığı:
    1. Aşama: Sunucunun kendi kayıt listesine (DNS_RECORDS) bakar.
       google.com, ktu.edu.tr, github.com vb. doğrudan bu listeden yanıtlanır.
    2. Aşama: DNS Önbelleğine (Cache) bakar.
    3. Aşama: Listede ve önbellekte yoksa, internetteki gerçek DNS hiyerarşisine
       (socket.gethostbyname) sorarak öğrenir ve önbelleğe ekler.
    """
    # 1. Aşama: Sunucunun Kendi Kayıt Listesi (Örn: google.com, ktu.edu.tr)
    if domain_name in DNS_RECORDS:
        return DNS_RECORDS[domain_name], "SUNUCU KENDİ LİSTESİ"

    # 2. Aşama: DNS Önbelleği (Cache)
    if domain_name in dns_cache:
        return dns_cache[domain_name], "ÖNBELLEK (CACHE HIT)"

    # 3. Aşama: Listede Olmayan Diğer Alan Adları İçin İnternetten Çözümleme
    try:
        # İşletim sistemi aracılığıyla gerçek internet DNS sunucularına sor
        real_ip = socket.gethostbyname(domain_name)
        # Öğrenilen yeni adresi gelecekteki sorgular için önbelleğe al
        dns_cache[domain_name] = real_ip
        return real_ip, "İNTERNET (RECURSIVE RESOLVE)"
    except socket.gaierror:
        # Böyle bir alan adı internette bulunamadı
        return None, "KAYIT BULUNAMADI (NXDOMAIN)"


def start_generic_dns_server():
    """
    Sunucunun ana çalışma döngüsü.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind((HOST, PORT))
        except OSError as e:
            print(f"[HATA] Port {PORT} dinlenemedi: {e}")
            return

        print("=" * 65)
        print("GENEL DNS SUNUCUSU BAŞLATILDI (Google DNS Benzeri Model)")
        print(f"Dinlenen Adres : {HOST}:{PORT} (UDP)")
        print(f"Tanımlı Kendi Kayıtları ({len(DNS_RECORDS)} Adet):")
        print(f"  {', '.join(list(DNS_RECORDS.keys())[:8])} ...")
        print("google.com gibi kayıtlar kendi listesinden, diğerleri internetten çözülür.")
        print("=" * 65)
        print("İstemcilerden sorgu bekleniyor...\n")

        try:
            while True:
                # İstemciden DNS sorgu paketini ve adresini al
                data, addr = s.recvfrom(512)

                # Alan adını ayrıştır
                domain = parse_dns_question(data)
                if not domain:
                    continue

                print(f"[{addr}] Sorgu: '{domain}'")

                # Alan adını çöz (Yerel -> Cache -> İnternet)
                resolved_ip, kaynak = resolve_domain(domain)

                if resolved_ip:
                    print(f"  -> Çözümlendi [{kaynak}]: {resolved_ip}")
                else:
                    print(f"  -> Çözümlenemedi [{kaynak}]")

                # İstemciye standart DNS yanıt paketini gönder
                response_packet = create_dns_response(data, resolved_ip)
                if response_packet:
                    s.sendto(response_packet, addr)

                print("-" * 50)

        except KeyboardInterrupt:
            print("\nSunucu kullanıcı tarafından kapatılıyor...")

        print("DNS sunucusu sonlandırıldı. Hoşça kalın!")


if __name__ == '__main__':
    start_generic_dns_server()
