import socket

# Sabit IP adresleri (yanıt olarak dönecek)
RESOLVED_IPS = {
    'google.com': '18.8.4.4',
    'github.com': '140.82.121.32',
    'www.ktu.edu.tr': '193.140.70.197'
}

def parse_dns_question(data):
    """
    DNS sorgu paketinden alan adını çıkarır.
    Paketin 'Question' bölümünü ayrıştırır.
    """
    # Header'ı atla (12 byte)
    question_start = 12
    domain_name = ""
    i = question_start
    while data[i] != 0:
        length = data[i]
        domain_name += data[i+1 : i+1+length].decode('ascii') + "."
        i += length + 1
    
    # Sondaki noktayı kaldır
    return domain_name.strip('.')

def create_dns_response(packet, ip_address):
    """
    Gelen sorgu paketini kullanarak bir DNS yanıt paketi oluşturur.
    """
    # 1. Başlık Bölümünü Oluştur (Header)
    header = packet[:2] # ID'yi koru
    
    # Bayrakları güncelle: QR=1 (yanıt), AA=1 (yetkili), RA=0
    flags = b'\x81\x80' # Özyineli sorgu yanıtı
    
    # QDCOUNT (soru sayısı)
    qdcount = packet[4:6]
    
    # ANCOUNT (cevap sayısı)
    ancount = b'\x00\x01' # Bir cevap döneceğiz
    
    # NSCOUNT ve ARCOUNT
    nscount = b'\x00\x00'
    arcount = b'\x00\x00'
    
    response_header = header + flags + qdcount + ancount + nscount + arcount
    
    # 2. Soru Bölümünü Ekle (Question)
    question_section_start = 12
    # Soru bölümünün sonunu bulmak için alan adının sonunu (0x00) ve ardından 4 byte (QTYPE/QCLASS) al
    question_end = packet.find(b'\x00', question_section_start) + 5
    question_section = packet[question_section_start:question_end]
    
    # 3. Cevap Bölümünü Oluştur (Answer)
    # DNS formatında alan adı işareti (pointer)
    name_pointer = b'\xc0\x0c' # Paketin 12. baytındaki alan adını işaret et
    
    # RDATA formatı (A kaydı için)
    record_type = b'\x00\x01' # A kaydı
    record_class = b'\x00\x01' # IN (Internet) sınıfı
    ttl = b'\x00\x00\x00\x1c' # Time to Live (TTL), 28 saniye
    data_length = b'\x00\x04' # RDATA (IP) uzunluğu, 4 byte
    rdata = socket.inet_aton(ip_address) # IP adresini bayt formatına dönüştür
    
    response_answer = name_pointer + record_type + record_class + ttl + data_length + rdata
    
    # Toplam yanıt paketini birleştir
    return response_header + question_section + response_answer

def run_dns_server(host='127.0.0.1', port=53):
    """
    Temel bir DNS sunucusu çalıştırır ve gelen sorgulara yanıt verir.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    
    print(f"DNS sunucusu {host}:{port} adresinde çalışıyor...")
    
    try:
        while True:
            print("Sorgu bekleniyor...")
            # Gelen sorgu paketini ve istemcinin adresini al
            data, addr = sock.recvfrom(512)
            
            # Gelen paketten alan adını ayrıştır
            domain_name = parse_dns_question(data)
            print(f"Sorgu alındı: '{domain_name}'")
            
            # Kayıtlı IP adresini bul
            ip_address = RESOLVED_IPS.get(domain_name, '127.0.0.1') # Yoksa 127.0.0.1 dön
            
            # Yanıt paketini oluştur
            response_packet = create_dns_response(data, ip_address)
            
            # Yanıtı istemciye geri gönder
            sock.sendto(response_packet, addr)
            print(f"Yanıt gönderildi: '{ip_address}'\n")

    except KeyboardInterrupt:
        print("Sunucu kapatılıyor...")
    finally:
        sock.close()

if __name__ == "__main__":
    run_dns_server()