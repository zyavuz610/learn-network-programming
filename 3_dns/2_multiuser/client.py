"""
Çok İstemcili Ortam İçin DNS İstemcisi (Multi-Client UDP Client)
--------------------------------------------------------------
Önemli Noktalar:
1. Çoklu İstemci Testi:
   - Bu istemci dosyasını birden çok terminal penceresinde ayrı ayrı çalıştırabilirsiniz
     (Terminal 1: İstemci A, Terminal 2: İstemci B vb.).
   - Her istemci soketi açtığında işletim sistemi ona farklı bir yerel port numarası
     (ephemeral port) atar. Sunucu da istemcileri bu port numaralarından tanır.

2. Gecikme Süresi (RTT - Round Trip Time):
   - İstemci paketi gönderdiği an ile yanıtı aldığı an arasındaki süreyi milisaniye (ms)
     olarak hesaplar.
   - İstemci 1 bir alanı ilk kez sorguladığında normal sürede yanıt alırken, İstemci 2
     aynı alanı sorguladığında sunucu önbelleğinden (Cache) çok daha hızlı yanıt döner.

3. Çıkış:
   - ':q' yazılarak istemci sonlandırılabilir.
"""
import socket
import time

# Sorgulanacak DNS sunucusunun IP adresi ve port numarası
DNS_SERVER_HOST = '127.0.0.1'
DNS_SERVER_PORT = 5353


def build_dns_query(domain_name):
    """
    Kullanıcının girdiği alan adı için RFC 1035 formatında DNS sorgu paketi üretir.
    """
    # 1. Başlık (Header - 12 Bayt): ID, RD=1 (Özyineli sorgu isteği), QDCOUNT=1
    header = b'\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'

    # 2. Soru Bölümü (Question)
    parts = domain_name.split('.')
    question_name = b''
    for part in parts:
        question_name += bytes([len(part)])
        question_name += part.encode('ascii')
    question_name += b'\x00'

    # QTYPE: 0x0001 (A Kaydı), QCLASS: 0x0001 (IN)
    qtype_qclass = b'\x00\x01\x00\x01'

    return header + question_name + qtype_qclass


def parse_dns_response(response):
    """
    DNS sunucusundan dönen bayt dizisinden IP adresini çözer.
    Kayıt bulunamadıysa (NXDOMAIN) None döner.
    """
    rcode = response[3] & 0x0F
    ancount = int.from_bytes(response[6:8], byteorder='big')

    if rcode == 3 or ancount == 0:
        return None

    # A kaydının IPv4 verisi yanıt paketinin son 4 baytındadır
    ip_bytes = response[-4:]
    return socket.inet_ntoa(ip_bytes)


def start_multiuser_dns_client():
    """
    DNS istemcisini başlatır ve kullanıcıdan alan adı sorguları alır.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Yanıt gelmemesi durumunda istemcinin kilitlenmesini önlemek için zaman aşımı
        s.settimeout(3.0)

        # İşletim sisteminin bu istemciye atadığı yerel portu öğrenmek için boş bir bind
        s.bind(('127.0.0.1', 0))
        yerel_ip, yerel_port = s.getsockname()

        print("=" * 65)
        print("Çok İstemcili DNS İstemcisine Hoş Geldiniz.")
        print(f"Bu İstemcinin Kimliği (Adresi): {yerel_ip}:{yerel_port}")
        print(f"Hedef DNS Sunucusu: {DNS_SERVER_HOST}:{DNS_SERVER_PORT}")
        print("Çıkmak için ':q' yazabilirsiniz.")
        print("=" * 65)

        sorgu_sayaci = 0

        while True:
            domain = input("\nSorgulanacak alan adı (Örn: ktu.edu.tr): ").strip()

            if not domain:
                continue

            if domain.lower() == ':q':
                print(f"İstemci ({yerel_port}) programı sonlanıyor. Hoşça kalın!")
                break

            sorgu_sayaci += 1
            query_packet = build_dns_query(domain)

            try:
                # Gönderim zamanını kaydet
                baslangic_zamani = time.time()

                # Sorguyu sunucuya gönder
                s.sendto(query_packet, (DNS_SERVER_HOST, DNS_SERVER_PORT))

                # Sunucudan yanıtı al
                response_data, _ = s.recvfrom(512)

                # Gidiş-dönüş süresi (Round Trip Time) milisaniye cinsinden
                gecen_sure_ms = (time.time() - baslangic_zamani) * 1000

                # Yanıtı çözümle
                ip_address = parse_dns_response(response_data)

                if ip_address:
                    print(f"[{sorgu_sayaci}. Sorgu - BAŞARILI]")
                    print(f"  Alan Adı   : {domain}")
                    print(f"  IP Adresi  : {ip_address}")
                    print(f"  Yanıt Süresi: {gecen_sure_ms:.2f} ms")
                else:
                    print(f"[{sorgu_sayaci}. Sorgu - BAŞARISIZ]")
                    print(f"  '{domain}' alan adı sunucuda bulunamadı (NXDOMAIN).")
                    print(f"  Yanıt Süresi: {gecen_sure_ms:.2f} ms")

            except socket.timeout:
                print(f"[HATA] Zaman aşımı: DNS sunucusundan ({DNS_SERVER_HOST}:{DNS_SERVER_PORT}) yanıt alınamadı!")
            except Exception as e:
                print(f"[HATA] Bir sorun oluştu: {e}")


if __name__ == '__main__':
    start_multiuser_dns_client()
