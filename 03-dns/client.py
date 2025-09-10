# pip install dnspython
import dns.resolver
import dns.exception

def resolve_domain(domain_name):
    """
    Belirtilen alan adının IP adresini (A kaydı) sorgular.
    """
    try:
        # Bir DNS çözümleyici (resolver) nesnesi oluştururuz.
        # Bu nesne, sisteminizin varsayılan DNS sunucularını kullanır.
        resolver = dns.resolver.Resolver()

        # 'A' kaydı, bir alan adının IPv4 adresini tutar.
        # DNS sunucusuna bu türden bir sorgu göndeririz.
        answers = resolver.resolve(domain_name, 'A')

        # Gelen yanıtlar bir liste halinde döner.
        # Her bir yanıt, bir A kaydı (IP adresi) içerir.
        ip_addresses = [str(a) for a in answers]
        
        return ip_addresses

    except dns.resolver.NoAnswer:
        # Sorgulanan alan adının A kaydı bulunamadığında oluşan hata
        print(f"Hata: '{domain_name}' alan adı için A kaydı bulunamadı.")
        return None
    except dns.resolver.NXDOMAIN:
        # Sorgulanan alan adının var olmadığı (domain not found) durumda oluşan hata
        print(f"Hata: '{domain_name}' böyle bir alan adı bulunmuyor.")
        return None
    except dns.exception.Timeout:
        # DNS sunucusundan yanıt alınamadığında oluşan hata
        print(f"Hata: DNS sunucusu zaman aşımına uğradı.")
        return None
    except Exception as e:
        # Diğer genel hatalar
        print(f"Beklenmeyen bir hata oluştu: {e}")
        return None

# Ana program döngüsü
print("Gerçek DNS Çözümleyiciye Hoş Geldiniz.")
print("Çıkmak için ':q' yazın.")

while True:
    domain_to_query = input("\nSorgulanacak alan adını girin: ")
    
    if domain_to_query.lower() == ':q':
        print("Programdan çıkılıyor...")
        break
    
    # Boş bir alan adı girilirse atla
    if not domain_to_query:
        continue

    # Fonksiyonu çağırarak IP adresini al
    ips = resolve_domain(domain_to_query)

    # IP adresleri varsa ekrana yazdır
    if ips:
        print(f"'{domain_to_query}' için bulunan IP adresleri:")
        for ip in ips:
            print(f"- {ip}")