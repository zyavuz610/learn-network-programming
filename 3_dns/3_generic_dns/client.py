"""
Genel DNS Sunucularından Sorgu Yapan İstemci (Generic / Public DNS Client)
========================================================================

Bu program, Python'ın yerleşik 'socket' kütüphanesini kullanarak herhangi bir
üçüncü parti kütüphaneye (dnspython vb.) ihtiyaç duymadan, doğrudan internetteki
genel (public) DNS sunucularına RFC 1035 standartlarında UDP sorguları gönderir.

NASIL KULLANILIR?
-----------------
1. Programı terminalden çalıştırın:
     python 3_dns/3_generic_dns/client.py

2. Karşınıza popüler genel DNS sunucularının listesi gelecektir:
     [1] Google DNS      (8.8.8.8)
     [2] Cloudflare DNS  (1.1.1.1)
     [3] Quad9           (9.9.9.9)
     [4] OpenDNS         (208.67.222.222)
     [0] Hız & Yanıt Karşılaştırması (Tüm sunuculara aynı anda sorgu atar)

3. Bir sunucu seçin veya [0] seçeneği ile tüm sunucuların yanıt sürelerini (RTT) kıyaslayın.
4. Çözümlemek istediğiniz alan adını girin (Örn: 'ktu.edu.tr', 'github.com', 'google.com').
5. Program sorguyu gönderir, geçen süreyi (milisaniye) ve dönen IP adres(ler)ini ekrana basar.
6. DNS sunucusunu değiştirmek için ':c', programdan çıkmak için ':q' yazabilirsiniz.

ÖNEMLİ NOT (Kurumsal / Üniversite Ağları):
----------------------------------------
Bazı üniversite (Eduroam / Kampüs) ve şirket güvenlik duvarları, dışarıdaki
8.8.8.8 veya 1.1.1.1 gibi DNS sunucularına doğrudan giden 53 nolu UDP portunu
engelleyebilir. Eğer genel sunuculardan zaman aşımı (timeout) alırsanız,
menüdeki 'Yerel Ağ / Modem DNS' seçeneğini kullanarak yerel ağ geçidiniz üzerinden
başarıyla sorgulama yapabilirsiniz.
"""
import socket
import time

# Popüler genel (public) DNS sunucuları (İsim, IP, Port)
PUBLIC_DNS_SERVERS = {
    '1': ('Google DNS', '8.8.8.8', 53),
    '2': ('Cloudflare DNS (En Hızlı)', '1.1.1.1', 53),
    '3': ('Quad9 (Zararlı Yazılım Korumalı)', '9.9.9.9', 53),
    '4': ('OpenDNS (Cisco)', '208.67.222.222', 53),
    '5': ('Yerel Ağ / Kampüs DNS Sunucusu', '192.168.4.66', 53),
    '6': ('Kendi Generic Sunucumuz (Localhost:5353)', '127.0.0.1', 5353),
}


def build_dns_query(domain_name):
    """
    Kullanıcının girdiği alan adı için RFC 1035 standardında 
    ikili (binary) DNS sorgu paketi üretir.
    """
    # 1. Başlık (Header - 12 Bayt):
    # Transaction ID: 0x1234
    # Flags: 0x0100 (Standart sorgu, RD=1 Özyineli sorgu isteği)
    # QDCOUNT: 1, ANCOUNT: 0, NSCOUNT: 0, ARCOUNT: 0
    header = b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'

    # 2. Soru Bölümü (Question Section):
    # Alan adını parçala ve her etiketin başına uzunluğunu ekle (Örn: \x03www\x03ktu\x03edu\x02tr\x00)
    parts = domain_name.strip('.').split('.')
    question_name = b''
    for part in parts:
        question_name += bytes([len(part)])
        question_name += part.encode('ascii')
    question_name += b'\x00'  # Soru isminin sonlandırıcı baytı

    # QTYPE: 0x0001 (A Kaydı - IPv4 adresi isteği)
    # QCLASS: 0x0001 (IN - Internet sınıfı)
    qtype_qclass = b'\x00\x01\x00\x01'

    return header + question_name + qtype_qclass


def parse_dns_response(data):
    """
    DNS sunucusundan dönen RFC 1035 paketini çözümleyerek
    A kayıtlarını (IPv4 adresleri) ve TTL süresini çıkarır.
    """
    if len(data) < 12:
        return {'status': 'HATA', 'message': 'Eksik veya geçersiz DNS yanıtı.'}

    # Header baytlarını oku
    rcode = data[3] & 0x0F  # Hata kodu (0: Başarılı, 3: NXDOMAIN)
    ancount = int.from_bytes(data[6:8], byteorder='big')  # Cevap sayısı

    if rcode == 3:
        return {'status': 'NXDOMAIN', 'message': 'Böyle bir alan adı bulunmuyor (NXDOMAIN).'}
    elif rcode != 0:
        return {'status': 'HATA', 'message': f'DNS Sunucu Hatası (RCODE: {rcode})'}

    if ancount == 0:
        return {'status': 'BOS', 'message': 'Bu alan adı için A (IPv4) kaydı bulunamadı.'}

    # Question (Soru) bölümünü atla
    idx = 12
    while idx < len(data) and data[idx] != 0:
        idx += data[idx] + 1
    idx += 5  # 0x00 sonlandırıcı + QTYPE (2) + QCLASS (2)

    ip_addresses = []
    ttl = None

    # Answer (Cevap) kayıtlarını tek tek ayrıştır
    for _ in range(ancount):
        if idx >= len(data):
            break

        # Alan adı göstergesi (Pointer mı yoksa normal etiket mi?)
        if data[idx] & 0xC0 == 0xC0:
            idx += 2  # 2 baytlık sıkıştırma pointer'ı (\xc0\x0c)
        else:
            while idx < len(data) and data[idx] != 0:
                idx += data[idx] + 1
            idx += 1

        # Kayıt alanları: TYPE (2), CLASS (2), TTL (4), RDLENGTH (2)
        rtype = int.from_bytes(data[idx : idx + 2], 'big')
        ttl = int.from_bytes(data[idx + 4 : idx + 8], 'big')
        rdlength = int.from_bytes(data[idx + 8 : idx + 10], 'big')
        idx += 10

        rdata = data[idx : idx + rdlength]
        idx += rdlength

        # Tip 1 = A Kaydı (IPv4), Uzunluk = 4 bayt
        if rtype == 1 and rdlength == 4:
            ip_addresses.append(socket.inet_ntoa(rdata))

    return {
        'status': 'OK',
        'ips': ip_addresses,
        'ttl': ttl,
    }


def query_single_dns(server_name, server_ip, domain_name, port=53, timeout=3.0):
    """
    Belirtilen genel DNS sunucusuna UDP üzerinden tek bir sorgu gönderir ve sonucu döner.
    """
    query_packet = build_dns_query(domain_name)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(timeout)
        try:
            start_time = time.time()
            s.sendto(query_packet, (server_ip, port))
            response_data, _ = s.recvfrom(1024)
            elapsed_ms = (time.time() - start_time) * 1000

            parsed = parse_dns_response(response_data)
            parsed['rtt_ms'] = elapsed_ms
            parsed['server_name'] = server_name
            parsed['server_ip'] = f"{server_ip}:{port}"
            return parsed

        except socket.timeout:
            return {
                'status': 'TIMEOUT',
                'message': 'Zaman aşımı (Sunucudan yanıt gelmedi veya port engelli).',
                'server_name': server_name,
                'server_ip': f"{server_ip}:{port}",
                'rtt_ms': None,
            }
        except Exception as e:
            return {
                'status': 'HATA',
                'message': str(e),
                'server_name': server_name,
                'server_ip': f"{server_ip}:{port}",
                'rtt_ms': None,
            }


def print_dns_menu():
    """
    Kullanıcıya seçebileceği genel DNS sunucularını listeler.
    """
    print("\n" + "=" * 65)
    print("GENEL (PUBLIC) DNS SUNUCULARI LİSTESİ:")
    print("=" * 65)
    for key, (name, ip, port) in PUBLIC_DNS_SERVERS.items():
        print(f"  [{key}] {name:<42} : {ip}:{port}")
    print("  [0] TÜMÜNÜ KARŞILAŞTIR (Hız ve IP Kıyaslama Testi)")
    print("=" * 65)


def start_generic_dns_client():
    """
    Genel DNS istemcisinin ana çalışma döngüsü.
    """
    print("*" * 65)
    print("  GENEL (PUBLIC) DNS ÇÖZÜMLEME İSTEMCİSİNE HOŞ GELDİNİZ")
    print("*" * 65)
    print("İnternetteki popüler DNS sunucularına doğrudan UDP sorgusu atar.")
    print("Komutlar: ':q' = Çıkış, ':c' = DNS Sunucusunu Değiştir\n")

    current_choice = '1'
    print_dns_menu()

    while True:
        choice = input(f"\nBir DNS sunucusu seçin [Varsayılan: {current_choice} - {PUBLIC_DNS_SERVERS[current_choice][0]}]: ").strip()
        if choice in PUBLIC_DNS_SERVERS or choice == '0':
            current_choice = choice
        elif choice.lower() == ':q':
            print("Program sonlandırılıyor. Hoşça kalın!")
            break
        elif choice != '':
            print("Geçersiz seçim, varsayılan sunucu kullanılıyor.")

        # Alan adı sorgulama döngüsü
        while True:
            if current_choice == '0':
                aktif_sunucu_adi = "Tüm Genel DNS Sunucuları (Karşılaştırma Modu)"
            else:
                s_name, s_ip, s_port = PUBLIC_DNS_SERVERS[current_choice]
                aktif_sunucu_adi = f"{s_name} ({s_ip}:{s_port})"

            print(f"\n[Aktif Sunucu: {aktif_sunucu_adi}]")
            domain = input("Sorgulanacak alan adı (Örn: ktu.edu.tr): ").strip()

            if not domain:
                continue

            if domain.lower() == ':q':
                print("Program sonlandırılıyor. Hoşça kalın!")
                return

            if domain.lower() == ':c':
                print_dns_menu()
                break  # Üst döngüye dönerek sunucu seçimi yaptır

            print(f"\n>>> '{domain}' sorgulanıyor...")

            # [0] Seçilmişse tüm sunucuları karşılaştır
            if current_choice == '0':
                print("-" * 65)
                print(f"{'DNS Sunucusu':<25} {'IP:Port':<22} {'Gecikme (RTT)':<15} {'Durum / Çözümlenen IP'}")
                print("-" * 65)

                for k, (s_name, s_ip, s_port) in PUBLIC_DNS_SERVERS.items():
                    res = query_single_dns(s_name, s_ip, domain, port=s_port)
                    rtt_str = f"{res['rtt_ms']:.2f} ms" if res['rtt_ms'] else "---"
                    server_loc = f"{s_ip}:{s_port}"

                    if res['status'] == 'OK':
                        ips_str = ", ".join(res['ips'][:2])
                        if len(res['ips']) > 2:
                            ips_str += f" (+{len(res['ips'])-2} IP)"
                        print(f"{s_name[:24]:<25} {server_loc:<22} {rtt_str:<15} {ips_str}")
                    else:
                        print(f"{s_name[:24]:<25} {server_loc:<22} {rtt_str:<15} [{res['status']}] {res['message']}")
                print("-" * 65)

            # Tek bir sunucu seçilmişse detaylı göster
            else:
                s_name, s_ip, s_port = PUBLIC_DNS_SERVERS[current_choice]
                res = query_single_dns(s_name, s_ip, domain, port=s_port)

                print("-" * 50)
                if res['status'] == 'OK':
                    print(f"[BAŞARILI] Yanıt Süresi: {res['rtt_ms']:.2f} ms")
                    print(f"Sunucu      : {res['server_name']} ({res['server_ip']})")
                    print(f"Alan Adı    : {domain}")
                    print(f"IP Adresleri: {', '.join(res['ips'])}")
                    if res['ttl']:
                        print(f"TTL (Ömür)  : {res['ttl']} saniye")
                elif res['status'] == 'TIMEOUT':
                    print(f"[ZAMAN AŞIMI] {res['server_name']} ({res['server_ip']}) yanıt vermedi.")
                    print("İpucu: Ağınızda genel 53 portu engellenmiş olabilir.")
                    print("      ':c' yazarak 'Yerel Ağ / Kampüs DNS' seçeneğini deneyebilirsiniz.")
                else:
                    print(f"[{res['status']}] {res['message']}")
                print("-" * 50)


if __name__ == '__main__':
    start_generic_dns_client()
