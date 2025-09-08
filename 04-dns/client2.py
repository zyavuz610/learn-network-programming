import socket

def get_ip_address_from_dns(domain_name, dns_server_ip):
    """
    Sadece soket kullanarak bir alan adının IP adresini bulur.
    Bu kod, sadece tek bir IP adresi bekler ve DNS protokolünün
    tüm karmaşıklıklarını ele almaz.
    """
    # DNS sorgu paketi (byte formatında)
    # Bu paket, google.com için sabit bir sorgudur
    # Header + Question bölümlerini içerir
    # 0x0100 -> QR=0, RD=1
    # google.com için QNAME: 6google3com0
    
    dns_query_packet = (
        b'\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' # Header
        b'\x06google\x03com\x00' # Question (qname)
        b'\x00\x01\x00\x01' # Question (qtype A, qclass IN)
    )
    
    # UDP soketi oluştur
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5) # 5 saniye bekleme süresi

    print(f"'{domain_name}' için DNS sunucusuna sorgu gönderiliyor...")
    
    try:
        # Sorgu paketini DNS sunucusuna gönder
        sock.sendto(dns_query_packet, (dns_server_ip, 53))
        
        # Sunucudan gelen yanıtı al
        response, _ = sock.recvfrom(4096)
        
        # IP adresinin başladığı yeri bul
        # Yanıt paketindeki IP adresi her zaman belirli bir yerdedir (eğer yanıt varsa)
        # Bu değer, paketin yapısına göre belirlenir ve sabittir.
        start_of_ip = 28 # Bu sayı, paket yapısına göre hesaplanmıştır
        
        # IP adresini 4 baytlık bölüm olarak al
        ip_bytes = response[start_of_ip : start_of_ip + 4]
        
        # Baytları okunabilir bir IP adresine dönüştür
        ip_address = socket.inet_ntoa(ip_bytes)
        
        print(f"\nIP Adresi: {ip_address}")
        
    except socket.timeout:
        print("Zaman aşımı hatası: DNS sunucusundan yanıt alınamadı.")
    except IndexError:
        print("Hata: Yanıt paketinde beklenen veri bulunamadı.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        sock.close()

# Örnek kullanım
dns_server_ip = '8.8.8.8' # Google'ın genel DNS sunucusu
get_ip_address_from_dns('google.com', dns_server_ip)
get_ip_address_from_dns('github.com', dns_server_ip)