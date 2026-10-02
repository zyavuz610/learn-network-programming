import poplib
import ssl
from email import parser
 
# POP3 sunucu bilgileri
# Çoğu servis için sunucu adresi ve port numaraları aşağıdaki gibidir:
# Gmail: pop.gmail.com (port 995)
# Outlook: outlook.office365.com (port 995)
# Yahoo: pop.mail.yahoo.com (port 995)
pop3_server = "pop.gmail.com"
port = 995
 
# Hesap bilgileri
email_address = "eposta_adresiniz@gmail.com"
password = "uygulama_sifreniz" # Uygulama şifresi kullanın
 
def main():
    try:
        print("POP3 sunucusuna bağlanılıyor...")
        # Güvenli (SSL/TLS) bağlantı kurma
        mail_server = poplib.POP3_SSL(pop3_server, port)
        
        # Sunucu karşılama mesajını al
        print(f"Sunucu: {mail_server.getwelcome().decode()}")
        
        # Kimlik doğrulama
        mail_server.user(email_address)
        mail_server.pass_(password)
        
        print("Giriş başarılı!")
        
        # Posta kutusu durumunu sorgulama (e-posta sayısı ve toplam boyut)
        num_messages, total_size = mail_server.stat()
        print(f"Posta kutusunda {num_messages} adet e-posta var. Toplam boyut: {total_size} bayt.")
        
        if num_messages > 0:
            # En son e-postanın numarasını al
            latest_message_number = num_messages
            print(f"İlk e-posta indiriliyor (No: {latest_message_number})...")
            
            # Belirtilen e-postayı indir
            # POP3'te e-postalar 1'den başlayarak numaralandırılır
            response, message_lines, octets = mail_server.retr(latest_message_number)
            
            # İndirilen veriyi birleştir ve e-posta nesnesine dönüştür
            # Her satır bir 'b' (byte) nesnesidir, string'e çevirmemiz gerekir
            message_content = b'\r\n'.join(message_lines).decode('utf-8')
            email_message = parser.Parser().parsestr(message_content)
            
            # E-posta başlıklarını yazdır
            print("\n--- İNDİRİLEN E-POSTA BİLGİLERİ ---")
            print(f"Gönderen: {email_message.get('From')}")
            print(f"Konu: {email_message.get('Subject')}")
            
            # E-posta gövdesini (metin kısmını) yazdır
            # Eğer e-posta birden fazla parçadan oluşuyorsa (metin/html/ek)
            # Metin parçasını bulup onu yazdırmayı deneriz.
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8')
                        print("\n--- E-POSTA İÇERİĞİ (Düz Metin) ---")
                        print(body)
                        break
            else:
                body = email_message.get_payload(decode=True).decode('utf-8')
                print("\n--- E-POSTA İÇERİĞİ (Düz Metin) ---")
                print(body)
            
            # İstenirse e-postayı sunucudan silme
            # mail_server.dele(latest_message_number)
            # print(f"\nE-posta No. {latest_message_number} silinmek üzere işaretlendi.")
            
        else:
            print("Posta kutunuzda okunacak yeni e-posta bulunmuyor.")
        
    except poplib.POP3.error_proto as e:
        print(f"POP3 protokolu hatası: {e}")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        # Bağlantıyı sonlandır
        if 'mail_server' in locals() and mail_server:
            mail_server.quit()
            print("\nBağlantı kapatıldı.")
 
if __name__ == "__main__":
    main()