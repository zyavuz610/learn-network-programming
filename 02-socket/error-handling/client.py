import socket

HOST = '127.0.0.1'
PORT = 12345  # Çalışmayan bir port numarası

try:
    # Soket oluşturuluyor ve bağlanılmaya çalışılıyor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Sunucuya başarıyla bağlanıldı.")
        # Bağlantı kurulduktan sonraki işlemler...

except ConnectionRefusedError:
    # Sunucu kapalı olduğu için bağlantı reddedildiğinde bu blok çalışır
    print("Hata: Sunucuya bağlanılamadı. Lütfen sunucunun çalıştığından emin olun.")

except TimeoutError:
    # Eğer sunucuya bağlanmak çok uzun sürerse bu hata fırlatılır
    print("Hata: Bağlantı zaman aşımına uğradı.")

except Exception as e:
    # Beklenmeyen diğer tüm hataları yakalamak için genel bir except bloğu
    print(f"Bilinmeyen bir hata oluştu: {e}")