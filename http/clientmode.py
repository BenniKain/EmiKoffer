import network
import utime
import gc
gc.collect()
print('Initial free: {} allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))
from GPIO_Pins import Steuerung
import urllib.urequest as urlreq

class Client:
    zeit = utime.time
    wificon = network.WLAN(network.STA_IF).isconnected
    ap = "192.168.4.1"
    
    @classmethod
    def setup(cls):
        Steuerung.setup()
        #damit mit server einheitlich
        cls.sensoraufruf, cls.postaufruf, cls.loggingaufruf  = cls.zeit(),cls.zeit(),cls.zeit()
        cls.sensorfreq,cls.postfreq,cls.loggingfreq = 1,5,60

    @classmethod
    def start(cls):
        try:
            while cls.wificon():
                if cls.zeit() > cls.sensoraufruf + cls.sensorfreq:
                    cls.sensoraufruf = cls.zeit()
                    Steuerung.read_DHT_data()
                    #Steuerung.read_BMP_Data()
                    print (Steuerung.datenDict) 
                
                if cls.zeit() > cls.postaufruf + cls.postfreq and network.WLAN(network.STA_IF).config("essid") =="Emi-Koffer":

                    print("send req")
                    response = urlreq.urlopen("http://{ip}/test".format(ip=cls.ap))
                    print( response)
                    #per http entsprechend der IP weiterleiten
                    #dafür wird die IP vom zugehörigen Koffer benötigt
                    #print("andere Url")
                if cls.zeit() > cls.loggingaufruf + cls.loggingfreq:
                    cls.loggingaufruf = cls.zeit()
                    zeit, datum = Steuerung.logging_Data()
                    print("Datengeloggt um {} am {}.".format(zeit,datum))

                cls.screenUpdate()

        except KeyboardInterrupt:
                print("Ende durch KeyboardInterrupt")
        
        finally:
            if not cls.wificon():
                print("wifi not connected")
                #asynchron wifimgr sollte das erledigen in boot datei

    @classmethod   
    def screenUpdate(cls):
        #screen soll entsprechend die werte wiedergeben
        Steuerung.updateScreen()


    #machine.reset()
if __name__ == "__main__":
    esp = Client
    esp.setup()
    esp.start()
