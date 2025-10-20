# server.py
import socket

# Sunucu ayarları
HOST = '127.0.0.1'  # Dinlenecek IP adresi
PORT = 12345        # Dinlenecek port
BUFFER_SIZE = 1024  # Alınacak maksimum veri boyutu

def udp_server():
    # AF_INET: IPv4 adresi ailesi, SOCK_DGRAM: UDP protokolü
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Soketi belirtilen IP ve Porta bağla
    server_socket.bind((HOST, PORT))
    print(f"UDP Sunucu {HOST}:{PORT} üzerinde dinlemede...")
    
    received_numbers = []
    
    while True:
        try:
            # recvfrom: Veri ve gönderici adresi (addr) beklenir
            data, addr = server_socket.recvfrom(BUFFER_SIZE)
            
            # Gelen veriyi (byte) string'e çevir ve sayıya dönüştür
            try:
                number = int(data.decode('utf-8').strip())
            except ValueError:
                # Geçersiz veri gelirse atla
                print(f"[UYARI] Geçersiz veri alındı: {data.decode('utf-8')}")
                continue
            
            # İstemciden gelen sayıyı kontrol et
            if number == -1:
                print(f"\n[BİTTİ] İstemciden sonlandırma sinyali (-1) alındı.")
                break  # Döngüden çık
            
            # Sayıyı listeye ekle
            received_numbers.append(number)
            print(f"Alındı: {number}")
            
        except Exception as e:
            print(f"Hata oluştu: {e}")
            break

    # Tüm sayılar alındıktan sonra sonuçları yazdır
    print("\n--- Alınan Tüm Sayılar (Gönderilme Sırasıyla) ---")
    if received_numbers:
        print(received_numbers)
    else:
        print("Hiç sayı alınamadı.")
        
    server_socket.close()
    print("Sunucu kapatıldı.")

if __name__ == '__main__':
    udp_server()