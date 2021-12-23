
#überschreibt um immer im client mode zu sein
import utime
#mit asynco könene mehrere tasks"gleichzeitig bearbeitet" werden
#am besten ein async main erstellen indem die task loop aufgerufen werden können
#diese main darf ebenfalls nie enden sollte aber nicht geloopt werden
#sonst werden immer wieder dieselben tasks erstellt.
#idealerweise mittels await task ein task am ende hinstellen die nie endet
 
def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def main():
    print("starte async Mode")
    set_global_exception()  # Debug aid
    asyncio.create_task(cleanup())
    asyncio.create_task(Steuerung.readData())  # Or you might do this
    asyncio.create_task(Steuerung.updateScreen())  # Or you might do this
    await asyncio.create_task(cleanup())  # Or you might do this + endlees loop

async def cleanup():
    while True:
        gc.collect()
        print("cleaned up")
        await asyncio.sleep(120)

#mode = "Testmode"

print(mode)

if mode == "ClientMode":
    from http.clientmode import Client
    cl=Client
    cl.setup()
    cl.start()
elif mode == "ServerMode":
    from http.httpServer import HttpServer
    server = HttpServer
    server.start_Server()
    print("Server gestartet")

elif mode=="Testmode":
    from steuerung.gpfile import Steuerung
    print("starte setup")
    Steuerung.setup()
    print("setup started")
    import uasyncio as asyncio
    try:
        print(" async starting")
        asyncio.run(main())
    finally:
        asyncio.new_event_loop()  # Clear retained state

