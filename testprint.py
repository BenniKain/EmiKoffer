import uasyncio

async def blink(led, period_ms):
    zeit  =time.time()
    while True:
        print("vergangene Zeit {}".format(time.time()-zeit))
        print("an")
        led.on()
        await uasyncio.sleep(2)        
        print("vergangene Zeit {}".format(time.time()-zeit))
        print("aus")
        led.off()
        await uasyncio.time.sleep(2)
        await uasyncio.time.sleep(0)

# Running on a generic board
from machine import Pin
#uasyncio.run(main(Pin(4)))
import time
loop = uasyncio.get_event_loop()
loop.create_task(blink(Pin(4), 5000)) # Schedule ASAP
loop.run_until_complete(blink(Pin(4), 5000))
while True:
    print("Pinvalue {}".format(Pin(4).value()))
    time.sleep(4)

