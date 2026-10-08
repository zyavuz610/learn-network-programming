import socket

# Sunucunun IP adresi ve port numarası
HOST = '127.0.0.1'
PORT = 65432

# İstemci bazlı toplamları saklamak için bir sözlük
client_totals = {}

# UDP soketi oluşturma
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"Sunucu {HOST}:{PORT} adresinde dinliyor...")
    
    while True:
        try:
            data, addr = s.recvfrom(1024)
            message = data.decode('utf-8')
            
            # Eğer istemci adresi sözlükte yoksa, yeni bir toplam başlat
            if addr not in client_totals:
                client_totals[addr] = 0
            
            # Çıkış mesajı kontrolü
            if message.lower() == ':q':
                total = client_totals.pop(addr)
                print(f"İstemci {addr} çıkış yaptı. Son toplam: {total}")
                
                # Toplamı istemciye geri gönder
                s.sendto(f"Toplam: {total}".encode('utf-8'), addr)
                continue
            
            try:
                number = int(message)
                client_totals[addr] += number
                current_total = client_totals[addr]
                
                print(f"[{addr}] Gelen sayı: {number} - Anlık toplam: {current_total}")
                
            except ValueError:
                print(f"[{addr}] Geçersiz mesaj: '{message}'")
                
        except Exception as e:
            print(f"Hata oluştu: {e}")
            break

print("Sunucu programı sonlanıyor.")