#from pwn import *
from threading import *
from time import *
from asyncio import *

sesje = {}

async def handler(reader,writer):
    addr = writer.get_extra_info('peername')
    print(f"[N] znaleziono połączenie z {addr}")
    sesje[addr] = writer
    try:
        writer.write(b'whoami')
        await writer.drain()
        odp = await reader.read(100)
        print(f"[I] kolega ma na imie {odp.decode().strip()}")
       
        while True:
            data = await reader.read(1024)
            if not data:
                break
        print(f"[{addr}] Otrzymano: {data.decode().strip()}")

    except Exception as e:
        print(f"exception: {e}")
    finally:
        print(f"[-] zamykanie {addr}")
        writer.close()
        await writer.wait_closed()
        if addr in sesje: del sesje[addr]

async def main():
    server = await start_server(handler,'0.0.0.0','4330')
    print("[+] Serwer został uruchomiony")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        pass