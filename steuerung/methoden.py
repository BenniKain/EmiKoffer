class steuersetup():
    @classmethod
    def get_ESPName(cls,esp_config_file,espID):
        try:
            import json
            print("open json")
            with open(esp_config_file, "r") as f:
                config = json.loads(f.read())
                for esps in config['known_ESP']:
                    #print(esps)
                    if esps["espID"] == espID:
                        name = esps["name"]
                        #print(name)
                        #cls.datenDict.update({"name":name})
                        return name
        except:
            print("ESP ID not found")

    @classmethod
    def get_espID(cls):
        import esp
        espID = str(esp.flash_id()) 
        return espID

    @classmethod
    def set_ds1306Time(cls):
        try:
            import ntptime
            ntptime.settime()                                                                   #settime von server Internet
            n = utime.localtime(utime.mktime(utime.localtime())+ 3600)  #+1 zeitverschiebung    #localtime      year,month,day,hour,minute,second,weekday, yearday
            return (n[0],n[1],n[2],0,n[3],n[4],n[5],0)                               #datetime ds    year,month,day,weekday,hour,min,second,subsecond
        except:
            pass

    @classmethod
    def sdcard(cls):
        pass
        """
        #sd card slot if needed not planned
        #inits SD Card holder
        #https://github.com/micropython/micropython/blob/a1bc32d8a8fbb09bc04c2ca07b10475f7ddde8c3/drivers/sdcard/sdcard.py    
        spisd = SoftSPI(-1, miso=Pin(12), mosi=Pin(13), sck=Pin(14))
        sd = SDCard(spisd, Pin(15))
        print('Root directory:{}'.format(os.listdir()))
        print(gc.mem_free()) 
        vfs = os.VfsFat(sd)        #zu wenig speicher um sd karte zu unterstüzen flo fragen
        os.mount(vfs, '/sd')
        os.chdir('sd')
        print('SD Card contains:{}'.format(os.listdir()))
        """

class oledanzeige():
    @classmethod
    def showWaage(cls,oled,hx711):
        oled.text('Gewicht g: :', 0, 0, 1)
        oled.text(str(hx711.read()),128-len(str(hx711.read()))*10, 0, 1)    #len is 4 trotz . wegen float daher 10 sign lang

    @classmethod
    def showValues(cls,oled,datenDict):
        oled.text('T C:', 0, 0, 1)
        oled.text(datenDict["temp"], 128-len(datenDict["temp"])*9, 0, 1)
        oled.text('Feuchte %:', 0, 14, 1)
        oled.text(datenDict["hum"],128-len(datenDict["hum"])*9,14,1)
        oled.text('Druck hPa:'.format(datenDict["press"]), 0, 28, 1)
        oled.text(datenDict["press"], 128-len(datenDict["press"])*9, 28, 1)
        oled.text('T C:', 0, 42, 1)
        oled.text(datenDict["tBMP"], 128-len(datenDict["tBMP"])*9, 42, 1)

    @classmethod
    def showIP(cls,oled,datenDict):
        oled.text('Name:', 0, 0, 1)
        oled.text(datenDict["name"], 128-len(datenDict["ip"])*9, 0, 1)  
        oled.text('IP:', 0, 14, 1)
        oled.text(datenDict["ip"], 128-len(datenDict["ip"])*9, 14, 1) 

class steuermethoden():
    @classmethod
    def update_Kofferdict(cls,dataDict):                #soll ein dictionary mit den esp updaten
        cls.kofferDict.update({dataDict["espID"]:dataDict}) #dict in dict quasi

    @classmethod
    def pumpeANAUS(cls,Pin):
        if Pin.value() == 0:
            print("Pumpe Aus")
            Pin.off()
            pumpenstatus = False
        elif Pin.value() == 1:
            print("Pumpe An")
            Pin.on()
            pumpenstatus = True
        return  pumpenstatus

    @classmethod
    def nextANzeige(cls,screenfeld,screenfelder):
        if screenfeld == screenfelder:
            screenfeld = 0
        else:
            screenfeld += 1 
        sleep(0.1)
        print("anzeige: {}".format(screenfeld))
        return screenfeld

    @classmethod
    def read_DHT_data(cls,dht11):
        try:
            dht11.measure()
            temp = str(dht11.temperature())
            hum = str(dht11.humidity())
        except:
            temp= "--"
            hum = "--"
        finally:
            return temp , hum

    @classmethod
    def read_BMP_Data(cls):
        try:
            tBMP    =   str(cls.bmp180.temperature)
            press   =   str(cls.bmp180.pressure /100)   #in Pa, mit /100 in hPa
            alt     =   str(cls.bmp180.altitude)
        except:
            tBMp,press,alt = "--","--","--"
        finally:
            return tBMP,press,alt

class TableErstellen:
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