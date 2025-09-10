import imaplib
import ssl
import email
from email.header import decode_header
 
# IMAP sunucu bilgileri
# Çoğu servis için sunucu adresi ve port numaraları aşağıdaki gibidir:
# Gmail: imap.gmail.com (port 993)
# Outlook: outlook.office365.com (port 993)
# Yahoo: imap.mail.yahoo.com (port 993)
imap_server = "imap.gmail.com"
port = 993
 
# Hesap bilgileri
email_address = "eposta_adresiniz@gmail.com"
password = "uygulama_sifreniz" # Uygulama şifresi kullanın
 
def main():
    try:
        print("IMAP sunucusuna bağlanılıyor...")
        # Güvenli (SSL/TLS) bağlantı kurma
        mail = imaplib.IMAP4_SSL(imap_server, port)
        
        # Kimlik doğrulama
        mail.login(email_address, password)
        print("Giriş başarılı!")
        
        # Klasörleri (posta kutularını) listeleme
        # Yanıt iki kısımdan oluşur: durum ve veri
        status, folders = mail.list()
        if status == 'OK':
            print("\n--- POSTA KUTUSU KLASÖRLERİ ---")
            for folder in folders:
                # Klasör adını doğru bir şekilde çözümle
                # Yanıt formatı: b'(\\HasNoChildren) "/" "INBOX"'
                folder_name = folder.decode().split('"')[-2]
                print(f"-> {folder_name}")
        
        # 'INBOX' klasörünü seç
        mail.select("INBOX")
        
        # 'ALL' kriteri ile tüm e-postaları ara
        # 'uid' parametresi ile UID numaralarını al
        status, email_ids = mail.uid('search', None, "ALL")
        if status != 'OK':
            print("E-posta arama hatası!")
            return
            
        # En son e-postanın UID'sini al
        latest_email_uid = email_ids[0].split()[-1]
        
        # E-posta başlıklarını (RFC822.HEADER) UID ile çek
        # 'peek' komutu ile e-postayı okundu olarak işaretlemeden indir
        status, email_data = mail.uid('fetch', latest_email_uid, '(RFC822.HEADER)')
        if status != 'OK':
            print("E-posta başlıklarını çekme hatası!")
            return
            
        raw_email = email_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        print("\n--- SON E-POSTA BİLGİLERİ ---")
        
        # E-posta başlıklarını çözümle ve yazdır
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")
        print(f"Konu: {subject}")
        
        from_, encoding = decode_header(msg["From"])[0]
        if isinstance(from_, bytes):
            from_ = from_.decode(encoding if encoding else "utf-8")
        print(f"Gönderen: {from_}")
        
        print(f"Tarih: {msg['Date']}")
        
    except imaplib.IMAP4.error as e:
        print(f"IMAP protokolu hatası: {e}")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        # Bağlantıyı kapat
        if 'mail' in locals() and mail:
            mail.logout()
            print("\nBağlantı kapatıldı.")
 
if __name__ == "__main__":
    main()