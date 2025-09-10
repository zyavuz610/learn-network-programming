import smtplib # SMTP protokolü için
import ssl # Güvenli bağlantı için
from email.mime.text import MIMEText # Düz metin e-posta için
from email.mime.multipart import MIMEMultipart # Çok parçalı e-posta için
 
# SMTP sunucu bilgileri
smtp_server = "smtp.gmail.com"
port = 587  # TLS için 587, SSL için 465
 
# Gönderen ve alıcı bilgileri
sender_email = "gonderen_emailiniz@gmail.com" # Gönderenin e-posta adresi, Gmail olabilir
password = "???" # Gmail uygulama şifresi olabilir
receiver_email = "alici_emailiniz@ornek.com" # Alıcının e-posta adresi
 
# E-posta içeriği
message = MIMEMultipart("alternative")
message["Subject"] = "Python ile E-posta Gönderme Örneği"
message["From"] = sender_email
message["To"] = receiver_email
 
# E-postanın düz metin ve HTML versiyonları
text = """Merhaba,
Bu e-posta Python smtplib modülü kullanılarak gönderilmiştir.
"""
html = """\
<html>
  <body>
    <p>Merhaba,<br>
       Bu e-posta <b>Python</b> ile gönderilmiştir.<br>
       <a href="https://www.python.org">Python web sitesi</a>
    </p>
  </body>
</html>
"""
 
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")
 
message.attach(part1)
message.attach(part2)
 
# SSL/TLS bağlantısı oluşturma
context = ssl.create_default_context()
 
try:
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)  # TLS'i başlat
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print("E-posta başarıyla gönderildi!")
except Exception as e:
    print(f"E-posta gönderilirken bir hata oluştu: {e}")