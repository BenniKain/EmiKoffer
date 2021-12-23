#from machine import Pin, SoftI2C,ADC,RTC,WDT,SoftSPI    #ESP8266 lib für GPIO etc.
from machine import Pin
from dht import DHT11                                   #feuchte und T sensor
#import ssd1306                                          #OLED Display
import gc, network,utime
from syncESP.steuerung.methoden import steuermethoden
#from Sensoren_lib.ds1307 import DS1307                  #Real time Clock
#from Sensoren_lib.bmp180 import  BMP180          #druck und t sensor
#from sdcard import SDCard                              #sdkarte braucht zu viel ram zu groß?

import uasyncio as asyncio

#enable garbage collector um arbeitsspeicher frei zu bekommen
gc.enable()
gc.collect()
print(gc.mem_free())

class Steuerung(): 
    PinNames = {"D3":0,"TX":1,"D4":2,
    "RX":3,"D2":4,"D1":5,"D6":12,
    "D7":13,"D5":14,"D8":15,"A0":0}
    pumpenrelay = Pin(PinNames["D2"],Pin.OUT)
    pumpentaster = Pin(PinNames["D7"],Pin.IN)                           #D7 (D8 is always pulled down geht nicht D3 und D4 pulled up always
    dht11 = DHT11(Pin(PinNames["D1"]))                                          #inits DHT sensor
    anzeigeschalter = Pin(PinNames["D3"],Pin.IN)
    datum = ".".join([str(char) for char in utime.localtime(utime.mktime(utime.localtime()) + 3600)[:3]])           #setzt datum inkl 1 h zeitverschiebung 
    zeit = ":".join([str(char) for char in utime.localtime(utime.mktime(utime.localtime()) + 3600)[3:6]])           #inits uhrzeit
    func ="Pumpe"
    #bmp180 = BMP180 (Pin(PinNames["D2"]))
    esp_config_file = "espconfig.json"     #für name am besten ein config file mit ID der ESPS als dict
    datenDict ={"temp":999,"hum":999,"tBMP":999,"press":0,"alt":999}
    loggingfilename = "/loggingdata/loggingfiles.txt"

    #inits SD Card holder
    #https://github.com/micropython/micropython/blob/a1bc32d8a8fbb09bc04c2ca07b10475f7ddde8c3/drivers/sdcard/sdcard.py
    """
    spisd = SoftSPI(-1, miso=Pin(12), mosi=Pin(13), sck=Pin(14))
    sd = SDCard(spisd, Pin(15))
    print('Root directory:{}'.format(os.listdir()))
    print(gc.mem_free()) 
    vfs = os.VfsFat(sd)        #zu wenig speicher um sd karte zu unterstüzen flo fragen
    os.mount(vfs, '/sd')
    os.chdir('sd')
    print('SD Card contains:{}'.format(os.listdir()))
    """

    @classmethod
    def setup(cls):
        print("Setup Steuerung")
        cls.pumpentaster.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING , handler=cls.pumpPinInterrupt)
        cls.anzeigeschalter.irq(trigger=Pin.IRQ_RISING , handler=cls.anzeigefenster)
        cls.get_IP()
        cls.get_espID()
        cls.get_ESPName()
        if network.WLAN(network.AP_IF).config("essid") == "Emi-Koffer":
            cls.kofferDict ={} 
        cls.screenfeld = 0          #für bildschirme zum iterieren von anzeigen
        cls.screenfelder = [i for i in range(3)]

    @classmethod
    def update_Kofferdict(cls,dataDict):
        cls.kofferDict.update({dataDict["espID"]:dataDict})  

    @classmethod
    def get_espID(cls):
        import esp
        espID = str(esp.flash_id())
        cls.datenDict.update({"espID":espID})  
        return espID

    @classmethod
    def get_ESPName(cls):
        try:
            import json
            print("open json")
            with open(cls.esp_config_file, "r") as f:
                config = json.loads(f.read())
                for esps in config['known_ESP']:
                    #print(esps)
                    if esps["espID"] == cls.datenDict["espID"]:
                        name = esps["name"]
                        #print(name)
                        cls.datenDict.update({"name":name})
                        return name
        except:
            print("ESP ID not found")

    @classmethod
    def pumpPinInterrupt(cls,Pin):
        cls.pumpenstatus = pumpeANAUS(Pin)

    @classmethod
    def get_IP(cls):
        if network.WLAN(network.STA_IF).config("essid") == "Emi-Koffer":
            cls.ip = network.WLAN(network.STA_IF).ifconfig()[0]                 #ip ist verbundene sta 
        elif network.WLAN(network.STA_IF).config("essid") != "Emi-Koffer":
            cls.ip = network.WLAN(network.AP_IF).ifconfig()[0]                  #ip ist accesspoint 
        cls.datenDict.update({"ip":cls.ip})  
        return cls.ip             
                
    @classmethod
    def read_DHT_data(cls):
        try:
            cls.dht11.measure()
            temp = str(cls.dht11.temperature())
            hum = str(cls.dht11.humidity())
        except:
            temp= "--"
            hum = "--"
        finally:
            cls.datenDict.update({"temp":temp,"hum":hum})

    @classmethod
    def read_DHT_data(cls):
        try:
            temp, hum = steuermethoden.readDHT(cls.dht11)
            cls.datenDict.update({"temp":temp,"hum":hum})
        except: 
            pass

    @classmethod
    def read_BMP_Data(cls):
        try:
            tBMP,press,alt= steuermethoden.readBMP(cls.bmp180)
            cls.datenDict.update({"tBMP":tBMP,"alt":alt,"press":press})        
        except:
            pass
            
    @classmethod
    async def read_BMP_Data(cls):
        try:
            tBMP    =   str(cls.bmp180.temperature)
            press   =   str(cls.bmp180.pressure /100)   #in Pa, mit /100 in hPa
            alt     =   str(cls.bmp180.altitude)
        except:
            tBMp,press,alt = "--","--","--"
        finally:
            cls.datenDict.update({"tBMP":tBMP,"alt":alt,"press":press})        
            print(cls.datenDict())
            await asyncio.sleep(5)
    
    @classmethod
    def logging_Data(cls):
        try:
            with open(cls.loggingfilename,"r")as f:
                pass
        except:
            with open(cls.loggingfilename,"w")as f:
                f.write("Datum:\tZeit\tT °C:\ttrel. Feuchte: %\n".format(datum = cls.datum,zeit = cls.zeit,temp=cls.datenDict["temp"],hum=cls.datenDict["hum"]))
        finally:
            cls.datum = ".".join([str(char) for char in utime.localtime(utime.mktime(utime.localtime()) + 3600)[:3]])           #setzt datum inkl 1 h zeitverschiebung 
            cls.zeit = ":".join([str(char) for char in utime.localtime(utime.mktime(utime.localtime()) + 3600)[3:6]])           #setzt uhrzeit inkl 1 h zeitverschiebung
            with open(cls.loggingfilename,"a")as f: 
                f.write("{datum}\t{zeit}\t{temp}\t{hum}\n".format(datum = cls.datum,zeit = cls.zeit,temp=cls.datenDict["temp"],hum=cls.datenDict["hum"]))
        return cls.zeit,cls.datum
    
    @classmethod
    def anzeigefenster(cls):
        cls.screenfeld +=1
        if cls.screenfeld > len(cls.screenfelder):
            cls.screenfeld = 0

    @classmethod
    def updateScreen(cls):
        pass
        if cls.screenfeld == 0:
            #print("zeige Par")
            cls.showValues()
        elif cls.screenfeld ==1:
            #print("zeige konfig")
            cls.showIP()
        elif cls.screenfeld ==2:
            #print("zeige Anderes")
            cls.showOther()
        

    @classmethod
    def showValues(cls):
        pass
    @classmethod
    def showIP(cls):
        pass
    @classmethod
    def showOther(cls):
        pass

    @classmethod
    def addRow(cls,liste):
        cls.tabellereihe = "<tr>"
        for i in liste:
            cls.tabellereihe += i
        cls.tabellereihe += "</tr>"
        return cls.tabellereihe

    @classmethod
    def get_table(cls):
        cls.DatenDict={}
        cls.DatenDict.update({"Parameter":("IP Adresse","Temperatur","Feuchtigkeit","Pumpe an","Pumpe aus")})
        cls.DatenDict.update({"{koffer}".format(koffer = cls.datenDict["koffer"]):["{ip}".format(ip=cls.datenDict["ip"]),cls.datenDict["temp"],cls.datenDict["hum"],
        "<a href=\"?Koffer={koffer}&ip={ip}&function={func}AN\"><button>einschalten</button></a>".format(koffer=cls.datenDict["koffer"],ip=cls.datenDict["ip"],func=cls.func),
        "<a href=\"?Koffer={koffer}&ip={ip}&function={func}AUS\"><button>ausschalten</button></a>".format(koffer=cls.datenDict["koffer"],ip=cls.datenDict["ip"],func=cls.func)]})
        #DatenDict.update({"Koffer2":("192.196.11.101",24,20,"<a href=\"?pin=Pumpe1ON\"><button>einschalten</button></a>","<a href=\"?pin=Pumpe1OFF\"><button>ausschalten</button></a>")})
        table = "<table><tr>"
        keys =list(cls.DatenDict.keys())
        for key in keys:
            table += "<th> {} </th>".format(key) 
        table += "</tr>"

        ipS,tS,humS,puANS,puAUSS =[],[] ,[],[],[]
        for key in keys:
            cls.ip,cls.T,cls.hum,cls.pupmeAN,cls.pumpeAUS = cls.DatenDict[key]
            ipS.append("<td> {}</td>".format(cls.ip))
            tS.append("<td>{}</td>".format(cls.T))
            humS.append("<td>{}</td>".format(cls.hum))
            puANS.append("<td>{}</td>".format(cls.pupmeAN))
            puAUSS.append("<td>{}</td>".format(cls.pumpeAUS))
        
        table += cls.addRow(ipS)
        table += cls.addRow(tS)
        table += cls.addRow(humS)
        table += cls.addRow(puANS)
        table += cls.addRow(puAUSS)
        table += "</table>"    
        return table

    @classmethod
    def query_verarbeiten (cls,parDict):
        if parDict["ip"] == cls.ip:
            print("eigener esp")
            commando = cls.functionCall(parDict["function"])
        else:   
            #import urllib.request as urlreq
            #urlreq.urlopen("http://{IP}/{commando}".format(IP=parDict["ip"],commando=parDict["function"]))
            #per http entsprechend der IP weiterleiten
            #dafür wird die IP vom zugehörigen Koffe benötigt
            print("andere Url")
            commando = cls.functionCall(parDict["function"])
            pass

        for i in parDict:
            print(i)
        return commando

    @classmethod
    def functionCall(cls,commando):
        if commando == "PumpeAN":
            cls.pumpe_an()      
        elif commando == "PumpeAUS":
            cls.pumpe_aus()
        return commando

if __name__ == "__main__":
    Steuerung.setup()