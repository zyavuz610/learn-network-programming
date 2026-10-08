"""
DNS (Domain Name System) İstemcisi (Tek Kullanıcılı / Temel Model)
-----------------------------------------------------------------
DNS İstemcisinin Çalışma Mantığı:
1. Sorgu Paketi Oluşturma (build_dns_query):
   - 12 baytlık standart DNS başlığı (Header) hazırlanır:
     * Transaction ID: İki baytlık rastgele veya sabit kimlik (örn: 0xAAAA).
     * Flags: 0x0100 (Standart sorgu, RD=1 Özyineli sorgu isteği).
     * QDCOUNT: 0x0001 (1 adet soru soruluyor).
   - Question bölümü eklenir:
     * Alan adı etiketlere bölünür ve her etiketin başına uzunluğu yazılır.
       (Örn: 'google.com' -> \x06google\x03com\x00)
     * QTYPE: 0x0001 (A Kaydı - IPv4 adresi isteği).
     * QCLASS: 0x0001 (IN - Internet sınıfı).

2. UDP ile İletim:
   - Sorgu paketi DNS sunucusuna (Varsayılan Port 53) UDP datagramı olarak gönderilir (sendto).
   - Sunucudan dönen yanıt paketi recvfrom() ile alınır.

3. Yanıtı Çözümleme (parse_dns_response):
   - Başlıktaki ANCOUNT (Cevap Sayısı) ve RCODE (Hata Kodu) kontrol edilir.
   - Eğer kayıt bulunmuşsa, paketin sonundaki 4 baytlık veri IPv4 adresine dönüştürülür.
"""
import socket

# Sorgulanacak DNS sunucusunun IP adresi ve port numarası
# Not: Standart DNS portu 53'tür ancak yerel testlerde çakışmaları önlemek için
# sunucuyla aynı şekilde 5353 portu kullanılır.
DNS_SERVER_HOST = '127.0.0.1'
DNS_SERVER_PORT = 5353


def build_dns_query(domain_name):
    """
    Kullanıcının girdiği alan adı için RFC 1035 formatında DNS sorgu paketi üretir.
    """
    # 1. Başlık (Header - 12 Bayt)
    # ID: 0xAAAA, Flags: 0x0100 (RD=1), QDCOUNT: 1, ANCOUNT: 0, NSCOUNT: 0, ARCOUNT: 0
    header = b'\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'

    # 2. Soru Bölümü (Question)
    # Alan adını parçala (örn: "google.com" -> ["google", "com"])
    parts = domain_name.split('.')
    question_name = b''
    for part in parts:
        question_name += bytes([len(part)])  # Parça uzunluğu (1 bayt)
        question_name += part.encode('ascii')  # Parçanın kendisi
    question_name += b'\x00'  # Alan adının bittiğini belirten 0 baytı

    # QTYPE: 0x0001 (A Kaydı), QCLASS: 0x0001 (IN)
    qtype_qclass = b'\x00\x01\x00\x01'

    return header + question_name + qtype_qclass


def parse_dns_response(response):
    """
    DNS sunucusundan dönen bayt dizisinden IP adresini çözer.
    Kayıt bulunamadıysa (NXDOMAIN) None döner.
    """
    # Yanıt kodunu (RCODE) kontrol et (Header 3. baytının son 4 biti)
    rcode = response[3] & 0x0F
    # Cevap sayısını (ANCOUNT) oku (Header 6 ve 7. baytlar)
    ancount = int.from_bytes(response[6:8], byteorder='big')

    # RCODE=3 ise alan adı bulunamamıştır (NXDOMAIN) veya cevap sayısı 0 ise
    if rcode == 3 or ancount == 0:
        return None

    # Basitlik için A kaydının IP verisinin paketin son 4 baytında yer aldığını kullanıyoruz
    ip_bytes = response[-4:]
    return socket.inet_ntoa(ip_bytes)


def start_dns_client():
    """
    DNS istemcisini başlatır ve kullanıcıdan alan adı sorguları alır.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Sunucu kapalıysa veya paket kaybolursa sonsuz beklememek için zaman aşımı:
        s.settimeout(3.0)

        print("=" * 60)
        print("DNS İstemcisine Hoş Geldiniz.")
        print(f"Hedef DNS Sunucusu: {DNS_SERVER_HOST}:{DNS_SERVER_PORT}")
        print("Çıkmak için ':q' yazabilirsiniz.")
        print("=" * 60)

        while True:
            domain = input("\nSorgulanacak alan adını girin (Örn: google.com): ").strip()

            if not domain:
                continue

            if domain.lower() == ':q':
                print("İstemci programı sonlanıyor. Hoşça kalın!")
                break

            # DNS sorgu paketini oluştur
            query_packet = build_dns_query(domain)

            try:
                # Sorguyu DNS sunucusuna gönder
                s.sendto(query_packet, (DNS_SERVER_HOST, DNS_SERVER_PORT))

                # Sunucudan yanıtı al
                response_data, _ = s.recvfrom(512)

                # Yanıtı çözümle
                ip_address = parse_dns_response(response_data)

                if ip_address:
                    print(f"[BAŞARILI] '{domain}' -> {ip_address}")
                else:
                    print(f"[BAŞARISIZ] '{domain}' alan adı sunucuda bulunamadı (NXDOMAIN).")

            except socket.timeout:
                print("[HATA] Zaman aşımı: DNS sunucusundan yanıt alınamadı. (Sunucu açık mı?)")
            except Exception as e:
                print(f"[HATA] Bir sorun oluştu: {e}")


if __name__ == '__main__':
    start_dns_client()
