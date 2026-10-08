"""
DNS (Domain Name System) Sunucusu (Tek Kullanıcılı / Temel Model)
-----------------------------------------------------------------
DNS Protokolü ve UDP İlişkisi:
1. Neden UDP (Port 53)?
   - DNS sorguları genellikle tek bir soru ve tek bir cevaptan oluşur (küçük boyutlu paketler).
   - TCP'nin 3'lü el sıkışma (3-way handshake) gecikmesi DNS için gereksiz bir ek yüktür.
   - Hızlı çözümleme (düşük gecikme süresi) amacıyla DNS varsayılan olarak UDP 53 portunu kullanır.

2. DNS Paket Yapısı (RFC 1035):
   - Header (Başlık - 12 Bayt): ID, Bayraklar (Flags - QR, Opcode, AA, RCODE), QDCOUNT, ANCOUNT vb.
   - Question (Soru Bölümü): Sorgulanan alan adı (QNAME), Kayıt türü (QTYPE - örn: A kaydı), Sınıf (QCLASS - IN).
   - Answer (Cevap Bölümü): Eşleşen IP adresi (RDATA), TTL (Yaşam süresi) vb.

3. Çalışma Mantığı:
   - Sunucu UDP soketi üzerinden istemciden 512 baytlık sorgu paketini alır.
   - Soru bölümünden sorgulanan alan adını ayrıştırır (parse_dns_question).
   - Sabit 10 adet DNS kaydı arasından IP adresini arar.
   - Bulursa IP ile (A kaydı), bulamazsa NXDOMAIN (Kayıt Bulunamadı) bayrağıyla DNS yanıt paketi üretip istemciye döner.
"""
import socket

# Sunucunun IP adresi ve port numarası
# Not: Standart DNS portu 53'tür; ancak yerel testlerde çakışma (WinError 10048) ve
# yönetici izni sorunlarını önlemek amacıyla burada 5353 portu tercih edilmiştir.
HOST = '127.0.0.1'
PORT = 5353

# Sunucuda kayıtlı 10 adet sabit DNS A (IPv4) kaydı
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


def parse_dns_question(data):
    """
    Gelen DNS sorgu paketindeki Question (Soru) bölümünden alan adını çıkarır.
    Format: [Uzunluk][Karakterler]...[0x00] (Örn: \x06google\x03com\x00)
    """
    question_start = 12  # İlk 12 bayt DNS Header'dır
    domain_parts = []
    i = question_start

    # 0x00 baytı alan adının bittiğini gösterir
    while i < len(data) and data[i] != 0:
        length = data[i]
        part = data[i + 1 : i + 1 + length].decode('ascii', errors='ignore')
        domain_parts.append(part)
        i += length + 1

    return ".".join(domain_parts).lower()


def create_dns_response(packet, ip_address=None):
    """
    Gelen sorgu paketini temel alarak RFC 1035 standartlarında bir DNS yanıt paketi oluşturur.
    """
    # --- 1. Başlık Bölümü (Header - 12 Bayt) ---
    transaction_id = packet[:2]  # İstemcinin gönderdiği Transaction ID korunmalıdır

    if ip_address:
        # QR=1 (yanıt), AA=1 (yetkili), RD=1, RA=1, RCODE=0 (Hata Yok - NoError)
        flags = b'\x81\x80'
        ancount = b'\x00\x01'  # 1 adet cevap dönüyoruz
    else:
        # RCODE=3 (NXDOMAIN - Domain bulunamadı), cevap yok
        flags = b'\x81\x83'
        ancount = b'\x00\x00'  # 0 adet cevap

    qdcount = packet[4:6]  # Soru sayısı (1)
    nscount = b'\x00\x00'  # Yetkili sunucu sayısı
    arcount = b'\x00\x00'  # Ek kayıt sayısı

    response_header = transaction_id + flags + qdcount + ancount + nscount + arcount

    # --- 2. Soru Bölümü (Question Section) ---
    # Soru bölümünün sonu: 0x00 sonlandırıcı baytından sonra gelen 4 bayttır (QTYPE + QCLASS)
    question_start = 12
    null_index = packet.find(b'\x00', question_start)
    if null_index == -1:
        return None
    question_end = null_index + 5
    question_section = packet[question_start:question_end]

    # Eğer IP adresi bulunamadıysa (NXDOMAIN), sadece Header + Question gönderilir
    if not ip_address:
        return response_header + question_section

    # --- 3. Cevap Bölümü (Answer Section - A Kaydı) ---
    name_pointer = b'\xc0\x0c'  # Soru kısmındaki alan adına işaret eden sıkıştırma pointer'ı
    record_type = b'\x00\x01'   # Tip: A (IPv4 Adresi)
    record_class = b'\x00\x01'  # Sınıf: IN (Internet)
    ttl = b'\x00\x00\x00\x3c'   # Time to Live (TTL): 60 saniye
    data_length = b'\x00\x04'   # IPv4 verisi 4 bayttır
    rdata = socket.inet_aton(ip_address)  # Metin IP'yi 4 bayt ikili veriye çevirir

    answer_section = name_pointer + record_type + record_class + ttl + data_length + rdata

    return response_header + question_section + answer_section


def start_dns_server():
    """
    DNS sunucusunu başlatır ve gelen sorguları dinler.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind((HOST, PORT))
        except OSError as e:
            print(f"[HATA] Port {PORT} bağlanamadı: {e}")
            print("Port başka bir program tarafından kullanılıyor olabilir veya izin gerekebilir.")
            return

        print("=" * 60)
        print(f"DNS Sunucusu {HOST}:{PORT} adresinde dinliyor (UDP)...")
        print(f"Sunucuda tanımlı sabit DNS kaydı sayısı: {len(DNS_RECORDS)}")
        print("=" * 60)

        try:
            while True:
                # İstemciden DNS sorgu paketini ve adresini al
                data, addr = s.recvfrom(512)

                # Alan adını ayrıştır
                domain_name = parse_dns_question(data)
                print(f"[{addr}] Sorgu alındı: '{domain_name}'")

                # Kayıtlı IP adresini ara
                ip_address = DNS_RECORDS.get(domain_name, None)

                if ip_address:
                    print(f"  -> Kayıt bulundu: {domain_name} -> {ip_address}")
                else:
                    print(f"  -> Kayıt bulunamadı (NXDOMAIN): {domain_name}")

                # Yanıt paketini üret
                response_packet = create_dns_response(data, ip_address)

                if response_packet:
                    # İstemciye DNS yanıt paketini gönder
                    s.sendto(response_packet, addr)

                print("-" * 40)

        except KeyboardInterrupt:
            print("\nDNS sunucusu sonlandırılıyor...")

        print("DNS sunucusu kapatıldı. Hoşça kalın!")


if __name__ == '__main__':
    start_dns_server()
