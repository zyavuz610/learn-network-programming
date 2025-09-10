from ftplib import FTP

# FTP sunucusuna bağlan
ftp = FTP('ftp.example.com')

# Kullanıcı adı ve şifre ile oturum aç
ftp.login(user='kullanici_adi', passwd='sifre')

# Bağlandığımız dizindeki dosyaları listele
print("Dizin içeriği:")
ftp.dir()

# Bir dosyayı indir
def indir_dosya(ftp_obj, dosya_adi):
    with open(dosya_adi, 'wb') as yerel_dosya:
        ftp_obj.retrbinary('RETR ' + dosya_adi, yerel_dosya.write)
    print(f"'{dosya_adi}' dosyası başarıyla indirildi.")

indir_dosya(ftp, 'test_dosyasi.txt')

# Bir dosyayı yükle
def yukle_dosya(ftp_obj, dosya_adi):
    with open(dosya_adi, 'rb') as yerel_dosya:
        ftp_obj.storbinary('STOR ' + dosya_adi, yerel_dosya)
    print(f"'{dosya_adi}' dosyası başarıyla yüklendi.")

# Örnek: 'test.py' adında bir dosya oluşturup yükleyelim
with open('test_yuklenecek.txt', 'w') as f:
    f.write('Bu dosya FTP ile yüklendi.')

yukle_dosya(ftp, 'test_yuklenecek.txt')

# FTP bağlantısını kapat
ftp.quit()