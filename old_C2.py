from pwn import *
import threading
import time

sesje = []
listen = listen(4330)

def handler(con):
    try:
        sesje.append(con)
        con.sendline(b'whoami')
        usr = con.recv(1024,timeout=2).decode().strip()
        host = con.rhost()
        print(f"nowe połączenie od {usr} na hoście {host}")
        while True:
            if con.closed:
                print(f"sesja od {usr} se umarła(adres ip: {host})")
            time.sleep(1)

    except Exception as e:
        print(f"wyjątek: {e}")
    finally:
        if con in sesje:
            sesje.remove(con)
        con.close()
        print(f"sesja od {usr} se umarła(adres ip: {host})")


