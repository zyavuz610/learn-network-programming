"""
Çok İstemcili DNS (Domain Name System) Sunucusu (Multi-Client UDP Server)
------------------------------------------------------------------------
Çalışma Mantığı ve Tek Kullanıcılı Versiyondan Farkları:
1. Çoklu İstemci Yönetimi (UDP Concurrency):
   - UDP bağlantısız (connectionless) bir protokol olduğu için tek bir soket üzerinden aynı anda onlarca farklı istemciden (farklı IP/Port ikililerinden) sorgu paketi gelebilir.
   - Sunucu, gelen her paketi `handle_client_query` fonksiyonu aracılığıyla ayrı bir
     iş parçacığına (threading.Thread) devreder. Böylece bir istemcinin sorgusu işlenirken
     diğer istemciler bloklanmaz.

2. Paylaşılan DNS Önbelleği (Shared DNS Cache):
   - Çok kullanıcılı sunucularda performans için önbellek (Cache) hayati önem taşır.
   - Bir istemci bir alan adını sorguladığında sonuç önbelleğe kaydedilir.
   - Başka bir istemci aynı adresi sorduğunda doğrudan önbellekten (Cache HIT) hızla yanıt verilir.
   - Thread güvenliği için önbelleğe erişimde `threading.Lock` kullanılır.

3. İstemci İstatistikleri ve İzleme (Client Tracking):
   - Sunucu hangi istemcinin (IP:Port) kaç adet sorgu yaptığını bellekte tutar ve konsola basar.
"""
import socket
import threading
import time

# Sunucunun IP adresi ve port numarası (Çakışmaları önlemek için 5353 seçilmiştir)
HOST = '127.0.0.1'
PORT = 5353

# Sunucuda tanımlı 10 adet sabit DNS A (IPv4) kaydı
DNS_RECORDS = {
    'google.com': '142.250.185.206',
    'github.com': '140.82.121.4',
    'ktu.edu.tr': '193.140.70.197',
    'youtube.com': '142.250.185.174',
    'wikipedia.org': '208.80.154.224',
    'python.org': '138.197.63.241',
    'stackoverflow.com': '151.101.65.69',
    'openai.com': '13.107.246.72',
    'microsoft.com': '20.112.52.29',
    'amazon.com': '205.251.242.103',
}

# Paylaşılan DNS önbelleği ve thread kilidi
# Format: { 'domain': ('ip_adresi', eklenme_zamani) }
dns_cache = {}
cache_lock = threading.Lock()

# İstemci istatistikleri ve thread kilidi
# Format: { (ip, port): toplam_sorgu_sayisi }
client_stats = {}
stats_lock = threading.Lock()


def parse_dns_question(data):
    """
    Gelen DNS sorgu paketindeki Question (Soru) bölümünden alan adını çıkarır.
    """
    question_start = 12
    domain_parts = []
    i = question_start

    while i < len(data) and data[i] != 0:
        length = data[i]
        part = data[i + 1 : i + 1 + length].decode('ascii', errors='ignore')
        domain_parts.append(part)
        i += length + 1

    return ".".join(domain_parts).lower()


def create_dns_response(packet, ip_address=None):
    """
    Gelen sorgu paketini temel alarak RFC 1035 standartlarında bir DNS yanıt paketi üretir.
    """
    # 1. Başlık Bölümü (Header - 12 Bayt)
    transaction_id = packet[:2]  # İstemcinin Transaction ID'si

    if ip_address:
        flags = b'\x81\x80'   # NoError (0), QR=1, AA=1, RD=1, RA=1
        ancount = b'\x00\x01' # 1 cevap
    else:
        flags = b'\x81\x83'   # NXDOMAIN (3 - Kayıt Yok)
        ancount = b'\x00\x00' # 0 cevap

    qdcount = packet[4:6]
    nscount = b'\x00\x00'
    arcount = b'\x00\x00'

    response_header = transaction_id + flags + qdcount + ancount + nscount + arcount

    # 2. Soru Bölümü (Question Section)
    null_index = packet.find(b'\x00', 12)
    if null_index == -1:
        return None
    question_section = packet[12 : null_index + 5]

    if not ip_address:
        return response_header + question_section

    # 3. Cevap Bölümü (Answer Section - A Kaydı)
    name_pointer = b'\xc0\x0c'
    record_type = b'\x00\x01'   # A Kaydı
    record_class = b'\x00\x01'  # IN Sınıfı
    ttl = b'\x00\x00\x00\x3c'   # 60 saniye TTL
    data_length = b'\x00\x04'   # 4 bayt IPv4
    rdata = socket.inet_aton(ip_address)

    answer_section = name_pointer + record_type + record_class + ttl + data_length + rdata

    return response_header + question_section + answer_section


def handle_client_query(sock, data, addr):
    """
    Her bir istemcinin sorgusunu ayrı bir iş parçacığında (thread) işler.
    Böylece çok istemcili ortamda hiçbir istemci diğerinin sorgusunu beklemez.
    """
    try:
        # İstemci istatistiğini güncelle
        with stats_lock:
            client_stats[addr] = client_stats.get(addr, 0) + 1
            sorgu_sirasi = client_stats[addr]

        # Paketten alan adını ayrıştır
        domain_name = parse_dns_question(data)
        print(f"[İSTEMCİ {addr}] #{sorgu_sirasi} Sorgu: '{domain_name}'")

        # 1. Önce Önbelleğe (Cache) Bak
        ip_address = None
        from_cache = False
        with cache_lock:
            if domain_name in dns_cache:
                ip_address = dns_cache[domain_name]
                from_cache = True

        # 2. Önbellekte yoksa sabit kayıtlara bak
        if not ip_address:
            ip_address = DNS_RECORDS.get(domain_name, None)
            if ip_address:
                # Bulunan kaydı gelecekteki istemciler için önbelleğe al
                with cache_lock:
                    dns_cache[domain_name] = ip_address

        # Durumu konsola yazdır
        if ip_address:
            kaynak = "ÖNBELLEK (CACHE HIT)" if from_cache else "ANA KAYIT (DATABASE)"
            print(f"  -> Çözümlendi [{kaynak}]: {domain_name} -> {ip_address}")
        else:
            print(f"  -> Bulunamadı (NXDOMAIN): {domain_name}")

        # Yanıt paketini üret ve istemciye gönder
        response_packet = create_dns_response(data, ip_address)
        if response_packet:
            sock.sendto(response_packet, addr)

    except Exception as e:
        print(f"[!] {addr} istemcisinin sorgusunda hata: {e}")


def start_multiuser_dns_server():
    """
    Çok istemcili DNS sunucusunu başlatır.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind((HOST, PORT))
        except OSError as e:
            print(f"[HATA] Port {PORT} bağlanamadı: {e}")
            return

        print("=" * 65)
        print(f"Çok İstemcili DNS Sunucusu {HOST}:{PORT} adresinde dinliyor (UDP)...")
        print(f"Tanımlı Sabit Kayıt Sayısı: {len(DNS_RECORDS)}")
        print("İş parçacığı (Multi-thread) ve Önbellek (Cache) desteği aktif.")
        print("=" * 65)

        try:
            while True:
                # Herhangi bir istemciden gelen sorgu paketini al
                data, addr = s.recvfrom(512)

                # Gelen her sorgu için yeni bir thread başlat (Asenkron / Eşzamanlı İşleme)
                worker = threading.Thread(
                    target=handle_client_query,
                    args=(s, data, addr),
                    daemon=True
                )
                worker.start()

        except KeyboardInterrupt:
            print("\nDNS sunucusu sonlandırılıyor...")

        print("DNS sunucusu kapatıldı. Hoşça kalın!")


if __name__ == '__main__':
    start_multiuser_dns_server()
