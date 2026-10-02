import socket
import time

def get_ip_address_from_dns(domain_name, dns_server_ip):
    """
    Dinamik olarak DNS sorgu paketi oluşturur ve IP adresini bulur.
    """
    # DNS Başlığı (Header, 12 byte): ID, Flags, QDCOUNT (sorgu sayısı) vb. içerir
    # Flags: 0x0100 -> QR=0 (sorgu), Opcode=0 (standart), AA=0, TC=0, RD=1 (özyineli sorgu isteniyor)
    header = b'\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'

    # Alan adını parçala ve DNS formatına dönüştür
    qname_parts = domain_name.split('.')
    qname_bytes = b''
    for part in qname_parts:
        # Her parçanın uzunluğunu 1 byte olarak ekle
        qname_bytes += bytes([len(part)])
        # Parçanın kendisini ASCII'ye dönüştürerek ekle
        qname_bytes += part.encode('ascii')
    qname_bytes += b'\x00' # Alan adının sonunu belirtir

    # Soru bölümü (Question): QNAME, QTYPE (A kaydı), QCLASS (IN)
    # 0x0001 -> A Kaydı, 0x0001 -> IN (Internet) Sınıfı
    question_section = qname_bytes + b'\x00\x01\x00\x01'

    # Toplam sorgu paketini oluştur
    dns_query_packet = header + question_section

    # UDP soketi oluştur
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)

    print(f"'{domain_name}' için DNS sunucusuna sorgu gönderiliyor: {dns_server_ip}")

    try:
        # Sorgu paketini gönder
        sock.sendto(dns_query_packet, (dns_server_ip, 53))

        # Yanıtı al
        response, _ = sock.recvfrom(4096)
        
        # Yanıt paketini çözümle
        # Cevap bölümü genellikle 12. bayttan sonra başlar
        # Ancak, soru bölümünün dinamik uzunluğu nedeniyle, paketin sonundan çözümlemek daha güvenlidir.
        # Basitlik için son 4 baytın IP adresi olduğunu varsayıyoruz (A kaydı için)
        
        # IP adresinin başladığı yeri bul
        # Header (12) + Question (dinamik) + Cevap Bölümü (minimum 16 bayt)
        # Cevap bölümündeki veri 4 bayttır, bu yüzden paketin sonundan 4. bayt
        start_of_ip = len(response) - 4
        
        # IP adresini 4 baytlık bölüm olarak al
        ip_bytes = response[start_of_ip:]
        
        # Baytları okunabilir bir IP adresine dönüştür
        ip_address = socket.inet_ntoa(ip_bytes)
        
        print(f"IP Adresi: {ip_address}", end="\n" + "-"*35 + "\n")

    except socket.timeout:
        print("Zaman aşımı hatası: DNS sunucusundan yanıt alınamadı.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        sock.close()

# Örnek kullanım
dns_server_ip = '8.8.8.8' # Google'ın genel DNS sunucusu
get_ip_address_from_dns('google.com', dns_server_ip)
time.sleep(1)
get_ip_address_from_dns('github.com', dns_server_ip)
time.sleep(1)
get_ip_address_from_dns('www.ktu.edu.tr', dns_server_ip)