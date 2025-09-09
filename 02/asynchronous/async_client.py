import asyncio
import sys

HOST = '127.0.0.1'
PORT = 8888

# Mesajları klavyeden okuyup sunucuya gönderen coroutine
async def send_message(writer):
    print("Mesajlaşmaya başlayabilirsiniz (çıkış için ':q' yazın).")
    while True:
        message = await asyncio.to_thread(input) # input() işlemi engellendiği için to_thread kullanıyoruz
        if message.lower() == ':q':
            writer.write(message.encode('utf-8'))
            await writer.drain()
            break
        
        writer.write(message.encode('utf-8'))
        await writer.drain()

    writer.close()
    await writer.wait_closed()
    print("Bağlantı kapatıldı.")
    
# Sunucudan gelen mesajları dinleyen coroutine
async def receive_message(reader):
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                print("Sunucu bağlantıyı kapattı.")
                break
            print(f"\n{data.decode('utf-8').strip()}")
    except asyncio.CancelledError:
        print("Okuma işlemi iptal edildi.")
    except Exception as e:
        print(f"Okuma sırasında hata oluştu: {e}")

# Ana istemci döngüsü
# Bu, eş zamanlı bir fonksiyon (coroutine) tanımlar. 
# Programın eş zamanlı olarak çalışacak ana giriş noktasıdır.
async def main():
    try:
        # Sunucuya Bağlantı Kurma
        reader, writer = await asyncio.open_connection(HOST, PORT)

        # İki görevi aynı anda çalıştır: mesaj gönderme ve mesaj alma
        # Görev Oluşturma ve Eş Zamanlı Çalıştırma
        send_task = asyncio.create_task(send_message(writer))
        receive_task = asyncio.create_task(receive_message(reader))

        # Görevlerin Beklenmesi ve Yönetilmesi
        done, pending = await asyncio.wait(
            [send_task, receive_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Tamamlanan görevi iptal et
        for task in pending:
            task.cancel()
            await task
            
    except ConnectionRefusedError:
        print("Hata: Sunucuya bağlanılamadı. Sunucunun çalıştığından emin olun.")

if __name__ == "__main__":
    asyncio.run(main())