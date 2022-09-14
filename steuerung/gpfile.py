from machine import Pin,SoftI2C,freq,PWM,ADC,reset
import uasyncio as asyncio
import utime,network
from dht import DHT11
from  ssd1306 import SSD1306_I2C                 #OLED Display
from Sensoren_lib.bmp180 import  BMP180          #druck und t sensor
from Sensoren_lib.ds1307 import DS1307  
from Sensoren_lib.hx711 import HX711
from steuerung.methoden import steuermethoden,steuersetup,oledanzeige

class Steuerung():
    freq(160000000)#setzt die frequenz der maschine auf den wert für hx711 waage laut beschreibung

    PinNames = {"D0":16,"D1":5,"D2":4,"D3":0,"D4":2,
    "D5":14,"D6":12,"D7":13,"D8":15,"A0":0,"TX":1,"RX":3}
    pumpenrelay = Pin(PinNames["D7"],Pin.OUT)
    pumpentaster = Pin(PinNames["D3"],Pin.IN)                                   #D7 D8 is always pulled down geht nicht D3 und D4 pulled up always
    waagen_taster = Pin(PinNames["D4"],Pin.IN)                                  #d8 is pulled up daher muss man mit vcc leiter
    hx711 = HX711(pd_sck=PinNames["D5"], dout=PinNames["D6"])                                           #inits waage hx711
    dht11 = DHT11(Pin(PinNames["D0"]))                                          #inits DHT sensor
    anzeigeschalter = Pin(PinNames["D8"],Pin.IN)    #d3 is pulled up daher muss man mit 0 leiter verbinden zum schalten
    i2c = SoftI2C(Pin(PinNames["D1"]),Pin(PinNames["D2"]))  #d1 ist scl d2 sca
    #i2c.init(Pin(PinNames["D1"]),Pin(PinNames["D2"]))

    #inits uhrzeit
    datum = ".".join([str(char) for char in utime.localtime(utime.mktime(utime.localtime()) + 3600)[:3]])           #setzt datum inkl 1 h zeitverschiebung 
    zeit = ":".join([str(char) for char in utime.localtime(utime.mktime(utime.localtime()) + 3600)[3:6]])
    try:
        bmp180 = BMP180 (i2c)
        bmpYN = True
        print("BMP180 gestartet")
    except:
        bmpYN = False
        print("BMP180 nicht gestartet")
    #ds = DS1307(i2c)
    try:
        oled = SSD1306_I2C(128, 64,i2c)
    except:
        "error Oled Display: rebooting now..."
        reset()

    esp_config_file = "espconfig.json"     #für name am besten ein config file mit ID der ESPS als dict
    datenDict ={"temp":"--","hum":"--","tBMP":"--","press":"--","alt":"--"}
    logfile = "/loggingdata/loggingfiles.txt"

    @classmethod
    def setup(cls):
        print("Setup Steuerung")
        cls.ledstärke = ADC(cls.PinNames["A0"])
        #cls.led=PWM(Pin(cls.PinNames["D4"]),duty =0,freq=1000)     #duty 0 = licht aus, max = 1023
        cls.pumpentaster.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING , handler=cls.pumpPinInterrupt)
        cls.anzeigeschalter.irq(trigger=Pin.IRQ_RISING , handler=cls.anzeigeInterrupt)
        cls.waagen_taster.irq(trigger=Pin.IRQ_RISING , handler=cls.waagentarInterrupt)
        cls.get_IP()
        cls.get_espID()
        cls.get_ESPName()
        if network.WLAN(network.AP_IF).config("essid") == "Emi-Koffer":
            cls.kofferDict ={} 
        cls.screenfeld = 1          #für bildschirme zum iterieren von anzeigen
        cls.screenfelder = [i for i in range(3)]

    @classmethod
    def get_espID(cls):
        espID = steuersetup.get_espID()
        cls.datenDict.update({"espID":espID})  
        print ( "ID des ESP's: ",espID)
        return espID

    @classmethod
    def get_ESPName(cls):
        name =steuersetup.get_ESPName(cls.esp_config_file, cls.datenDict["espID"])
        cls.datenDict.update({"name":name})
        print ("Name des ESP's: ", name)
        return name

    @classmethod
    def set_ds1306Time(cls):
        try:
            zeit = steuersetup.set_ds1306Time()
            cls.ds.datetime(zeit)                                #datetime ds    year,month,day,weekday,hour,min,second,subsecond
        except:
            pass

    def set_localtime(cls):
        n = cls.ds.datetime()                                                    #localtime      year,month,day,hour,minute,second,weekday, yearday
        utime.localtime(utime.mktime((n[0],n[1],n[2],n[4],n[5],n[6],0,0)))       #datetime ds    year,month,day,weekday,hour,min,second,subsecond

    @classmethod
    def get_IP(cls):
        essid =network.WLAN(network.STA_IF).config("essid")
        if essid == "Emi-Koffer":
            cls.ip = network.WLAN(network.STA_IF).ifconfig()[0]                 #ip ist verbundene sta 
        elif essid != "Emi-Koffer":
            cls.ip = network.WLAN(network.AP_IF).ifconfig()[0]                  #ip ist accesspoint 
        cls.datenDict.update({"ip":cls.ip})  
        return cls.ip             

    @classmethod
    def pumpPinInterrupt(cls,Pin):
        print("Pumpenstatus ändern Interrupt")
        cls.pumpenstatus = steuermethoden.pumpeANAUS(Pin,cls.pumpenrelay)
        utime.sleep(0.3)

    @classmethod
    def anzeigeInterrupt(cls,Pin):
        print("Nächste Anzeige Interupt")
        cls.screenfeld = steuermethoden.nextANzeige(cls.screenfeld,cls.screenfelder)

    @classmethod
    def waagentarInterrupt(cls,Pin):
        print("Tare")
        cls.hx711.tare()
 
    @classmethod
    async def readData(cls):
        while True:
            try:
                temp,hum = steuermethoden.read_DHT_data(cls.dht11)
                cls.datenDict.update({"temp":temp,"hum":hum})
                if cls.bmpYN:
                    tBMP,press,alt = steuermethoden.read_BMP_Data(cls.bmp180)
                    cls.datenDict.update({"tBMP":tBMP,"alt":alt,"press":press})
            except Exception as e:
                print("Fehler bei ReadData Methode: ", e)
                #raise e
            finally:
                print("Daten upgedated: ",cls.datenDict)
                await asyncio.sleep(5)

    @classmethod
    async def updateScreen(cls):
        while True:
            try:
                cls.oled.fill(0) 
                if   cls.screenfeld == 1:
                    oledanzeige.showValues(cls.oled,cls.datenDict)
                elif cls.screenfeld == 2:
                    oledanzeige.showWaage(cls.oled,cls.hx711)
                elif cls.screenfeld == 3:
                    oledanzeige.showIP(cls.oled,cls.datenDict)
                cls.oled.text("Seite: {}".format(cls.screenfeld),0,56,1)
                cls.oled.show()
            except:
                pass
            await asyncio.sleep_ms (200)