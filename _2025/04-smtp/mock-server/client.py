import socket

HOST = '127.0.0.1'  # Sunucunun adresi
PORT = 2525         # Sunucunun portu

# E-posta bilgileri
sender = 'sender@example.com'
recipient = 'recipient@example.com'
subject = 'Test Subject'
body = 'This is a test email sent using raw sockets.'

def receive_response(sock):
    """Soketten gelen yanıtı okur ve ekrana yazdırır."""
    data = sock.recv(1024).decode('utf-8')
    print(f"Sunucu: {data.strip()}")
    return data

def main():
    # TCP soketi oluştur
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Sunucuya bağlan
        client_socket.connect((HOST, PORT))
        print("Sunucuya bağlanıldı.")
        
        # Sunucu başlangıç mesajını al
        receive_response(client_socket)
        
        # HELO komutu
        client_socket.sendall(f'HELO mydomain.com\r\n'.encode('utf-8'))
        receive_response(client_socket)
        
        # MAIL FROM komutu
        client_socket.sendall(f'MAIL FROM:<{sender}>\r\n'.encode('utf-8'))
        receive_response(client_socket)
        
        # RCPT TO komutu
        client_socket.sendall(f'RCPT TO:<{recipient}>\r\n'.encode('utf-8'))
        receive_response(client_socket)
        
        # DATA komutu
        client_socket.sendall(f'DATA\r\n'.encode('utf-8'))
        receive_response(client_socket)
        
        # E-posta içeriği
        full_email = (
            f'From: <{sender}>\r\n'
            f'To: <{recipient}>\r\n'
            f'Subject: {subject}\r\n'
            f'\r\n'
            f'{body}\r\n'
            f'.\r\n' # E-posta içeriğinin sonu
        )
        client_socket.sendall(full_email.encode('utf-8'))
        receive_response(client_socket)
        
        # QUIT komutu
        client_socket.sendall(f'QUIT\r\n'.encode('utf-8'))
        receive_response(client_socket)
        
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        # Bağlantıyı kapat
        client_socket.close()
        print("Bağlantı kapatıldı.")

if __name__ == "__main__":
    main()