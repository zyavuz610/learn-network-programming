# client.py
import socket
import time

# Sunucu ayarları
HOST = '127.0.0.1'  # Sunucunun IP adresi
PORT = 12345        # Sunucunun portu

def udp_client():
    # AF_INET: IPv4 adresi ailesi, SOCK_DGRAM: UDP protokolü
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    server_address = (HOST, PORT)
    
    print(f"Sunucuya ({HOST}:{PORT}) veri göndermeye başlanıyor...")
    
    # 1'den 100'e kadar sayıları gönder
    for i in range(1, 1001):
        message = str(i)
        
        # Sayıyı byte'a çevirip sunucuya gönder
        client_socket.sendto(message.encode('utf-8'), server_address)
        print(f"Gönderildi: {i}")
        
        # Ağ tıkanıklığını azaltmak ve verileri daha rahat gözlemlemek için kısa bir bekleme
        time.sleep(0.01) 
        
    # Sonlandırma sinyali olan -1'i gönder
    print("\nSonlandırma sinyali (-1) gönderiliyor...")
    final_message = "-1"
    client_socket.sendto(final_message.encode('utf-8'), server_address)
    print("Gönderim tamamlandı.")

    client_socket.close()

if __name__ == '__main__':
    udp_client()