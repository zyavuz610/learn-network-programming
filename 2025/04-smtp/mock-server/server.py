import socket
import threading

HOST = '127.0.0.1'  # Yerel sunucu
PORT = 2525         # Deneme için farklı bir port kullanıyoruz

def handle_client(conn, addr):
    print(f"[{addr}] Bağlantı kabul edildi.")
    # Sunucu başlangıç mesajı
    conn.sendall(b'220 Mock SMTP Server Ready\r\n')
    
    while True:
        data = conn.recv(1024).decode('utf-8').strip() # Veriyi al ve decode et
        if not data:
            break
        
        print(f"[{addr}] İstemci: {data}")
        
        # Gelen komuta göre yanıt ver
        command = data.split(' ')[0].upper() # Komutu al
        
        if command == 'HELO' or command == 'EHLO':
            response = b'250 Hello\r\n'
        elif command == 'MAIL': # MAIL FROM komutu
            response = b'250 Ok\r\n'
        elif command == 'RCPT': # RCPT TO komutu
            response = b'250 Ok\r\n'
        elif command == 'DATA':
            response = b'354 Start mail input; end with <CRLF>.<CRLF>\r\n'
        elif data == '.': # DATA komutunun sonu
            response = b'250 Ok: message accepted for delivery\r\n'
        elif command == 'QUIT':
            response = b'221 Bye\r\n'
            conn.sendall(response)
            break
        else:
            response = b'500 Syntax error, command unrecognized\r\n'
        
        conn.sendall(response)
    
    print(f"[{addr}] Bağlantı kapatıldı.")
    conn.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP soketi
    server_socket.bind((HOST, PORT)) # Soketi belirtilen IP ve porta bağla
    server_socket.listen(5) # Gelen bağlantıları dinle (5 bağlantı sıraya alınabilir)
    print(f"Dinleme başladı: {HOST}:{PORT}") # Sunucu başlangıç mesajı
    
    while True:
        conn, addr = server_socket.accept() # Gelen bir bağlantıyı kabul et
        client_thread = threading.Thread(target=handle_client, args=(conn, addr)) # Yeni bir iş parçacığı oluştur
        client_thread.start() # İş parçacığını başlat

if __name__ == "__main__":
    main()