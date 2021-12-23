# This file is executed on every boot (including wake-boot from deepsleep)
import gc

gc.collect()
gc.enable()
print('Initial free: {} allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))
from wifimgr import WifiManager

wifimgr = WifiManager
wifimgr.setup_network()

try:
    import ntptime
    ntptime.settime() # set the rtc datetime from the remote server geht eine stunde falsch wegen zeitverschiebung. rtc.dattime nimmt komisches argument, nicht geschafft
    print("System-Uhrzeit eingestellt")
except:
    pass

wifimgr().start_managing()


print("Station IP:    \t{}".format(wifimgr.wlan().config("essid")), wifimgr.wlan().ifconfig()[0])
print("Accesspoint IP:\t{}".format(wifimgr.accesspoint().config("essid")), wifimgr.accesspoint().ifconfig()[0])

if wifimgr.wlan().config("essid") == wifimgr.ap_config["config"]["essid"]:
    mode= "ClientMode"
    print("Starte ClientMode")
    #nicht der server da da das verbundene wlan der accesspoint anderer esps ist
elif wifimgr.accesspoint().config("essid") == wifimgr.ap_config["config"]["essid"]:
    mode = "ServerMode"

    print("Starte ServerMode")
    #starte den server da accesspoint geöffnet wurde
    #server.start_server()
