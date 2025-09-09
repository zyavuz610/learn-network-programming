import asyncio
import socket

# Sunucunun adresi ve portu
HOST = '127.0.0.1'
PORT = 8888

# Bağlı istemcileri tutmak için bir küme (set) kullanıyoruz
clients = set()

# İstemciden gelen mesajları alıp diğer istemcilere yayınlayan coroutine
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    clients.add(writer)
    print(f"İstemci {addr} bağlandı.")
    
    try:
        while True:
            # İstemciden veri gelene kadar bekle, ancak bu sırada diğer işleri yap
            data = await reader.read(1024)
            message = data.decode('utf-8')

            if not message:
                break
            
            print(f"[{addr}] Gelen mesaj: {message.strip()}")

            if message.strip().lower() == ':q':
                print(f"İstemci {addr} çıkış yaptı.")
                break

            # Gelen mesajı tüm bağlı istemcilere yayınla
            broadcast_message = f"[{addr}]: {message.strip()}".encode('utf-8')
            for client in clients:
                if client is not writer: # Mesajı gönderen istemciye geri gönderme
                    client.write(broadcast_message)
                    await client.drain() # Verinin tamamen gönderilmesini bekle
                    
    except ConnectionResetError:
        print(f"İstemci {addr} aniden bağlantıyı kesti.")
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        print(f"İstemci {addr} bağlantısı kapatılıyor.")
        clients.remove(writer)
        writer.close()
        await writer.wait_closed()

# Ana sunucu döngüsü
# main adında bir Coroutine tanımlar. 
# async anahtar kelimesi, bu fonksiyonun doğrudan çağrılamayacağını, 
#  yalnızca asyncio.run() gibi bir olay döngüsü (event loop) içinde çalıştırılabileceğini belirtir.
async def main(): 
    # Sunucuyu Başlatma
    server = await asyncio.start_server(
        handle_client, # asyncio, her yeni bağlantı için handle_client coroutine'ini otomatik olarak başlatır
        HOST, 
        PORT
    )

    # Sunucu Adresini Ekrana Yazdırma    
    addr = server.sockets[0].getsockname()
    print(f"Sohbet sunucusu {addr} adresinde çalışıyor...")

    # Sonsuz Sunucu Döngüsü
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Sunucu sonlandırılıyor...")