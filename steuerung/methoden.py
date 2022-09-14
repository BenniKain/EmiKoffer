from time import sleep
class steuersetup():
    @classmethod
    def get_ESPName(cls,esp_config_file,espID):
        try:
            import json
            print("überprüfe ob ESP bereits in ESPconfig.json")
            with open(esp_config_file, "r") as f:
                config = json.loads(f.read())
                for esps in config['known_ESP']:
                    if esps["espID"] == espID:
                        name = esps["name"]
                        return name
        except:
            print("ESP ID not found")
        name = cls.saveNewESP(esp_config_file,config,espID)
        return name
    @classmethod
    def get_espID(cls):
        import esp
        espID = str(esp.flash_id()) 
        return espID

    @classmethod
    def saveNewESP(cls,esp_config_file,config,espID):
        import json
        print(" Speichere neuen ESP in JSON File")
        nummer = len(config["known_ESP"])+1
        config["known_ESP"].append(		{
			"espID": espID,
			"name": "Koffer{}".format(str(nummer)),
			"mode": "Koffer"})
        #speichern der geänderten var als Json datei
        with open(esp_config_file,"w")as f:
            json.dump(config,f)
        return str(nummer)
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

class LedLIcht:
    def lichtint (self,**kwargs):
        licht_in_prozent = int(kwargs["lichtintensity"]*(1023/100))  #1023/100 ist 8 bit zu prozent
        print("Lichtintensität auf {} geändert".format(licht_in_prozent))
        return  licht_in_prozent

class oledanzeige():
    @classmethod
    def showWaage(cls,oled,hx711):
        oled.text('Waagen anzeige:', 0, 0, 1)
        oled.text('Gewicht g: :', 0, 14, 1)
        oled.text(str(hx711.read()),128-len(str(hx711.read()))*10, 14, 1)    #len is 4 trotz . wegen float daher 10 sign lang
        oled.text("Tare auf ", 0, 28, 1)
        oled.text(str(hx711.read()),128-len(str(round(hx711.offset,1)))*10, 28, 1) 
        print(hx711.read())

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
        oled.text(datenDict["name"], 128-len(datenDict["name"])*9, 0, 1)  
        oled.text('IP:', 0, 14, 1)
        oled.text(datenDict["ip"], 128-len(datenDict["ip"])*9, 14, 1) 

class steuermethoden():
    @classmethod
    def update_Kofferdict(cls,dataDict):                #soll ein dictionary mit den esp updaten
        cls.kofferDict.update({dataDict["espID"]:dataDict}) #dict in dict quasi

    @classmethod
    def pumpeANAUS(cls,Pin,pumpenrelay):
        print("value of the InterruptPin: ",Pin.value())
        if Pin.value() == 0:
            print("Pumpe An")
            pumpenrelay.on()
            pumpenstatus = False
        elif Pin.value() == 1:
            print("Pumpe Aus")
            pumpenrelay.off()
            pumpenstatus = True
        return  pumpenstatus

    @classmethod
    def nextANzeige(cls,screenfeld,screenfelder):
        if screenfeld == len(screenfelder):
            screenfeld = 1
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
        except Exception as e:
            temp= "--"
            hum = "--"
            print(e)
        finally:
            return temp , hum

    @classmethod
    def read_BMP_Data(cls,bmp180):
        try:
            tBMP    =   str(round(bmp180.temperature,1))
            press   =   str(int(bmp180.pressure /100))   #in Pa, mit /100 in hPa
            alt     =   str(round(bmp180.altitude /100,0))
        except Exception as e:
            tBMP,press,alt = "--","--","--"
            print(e)
        finally:
            return tBMP,press,alt

class TableErstellen:
    @classmethod
    def get_table(cls,datenDict):
        func = "Nix"
        tabledict = {}
        tabledict.update({"Parameter":("IP Adresse","Temperatur","Druck","Feuchtigkeit","Pumpe an","Pumpe aus"  )})
        #,"LichtIntensität","Licht ändern")})
        tabledict.update({datenDict["name"]:[datenDict["ip"],datenDict["temp"],datenDict["press"],datenDict["hum"],
        "<a href=\"?Koffer={koffer}&ip={ip}&function={func}AN\"><button>einschalten</button></a>".format(koffer=datenDict["name"],ip=datenDict["ip"],func=func),
        "<a href=\"?Koffer={koffer}&ip={ip}&function={func}AUS\"><button>ausschalten</button></a>".format(koffer=datenDict["name"],ip=datenDict["ip"],func=func) ]})
        #,'<INPUT TYPE="password" NAME="Lichtintensity" SIZE="25">',
        #'<INPUT TYPE="SUBMIT" VALUE="Submit" NAME="B1">' ]})
        #anzeige von input feldern fuktioniert über esp nicht, warum auch immer

        table = "<table><tr>"
        keys =list(tabledict.keys())
        for key in keys:
            table += "<th> {} </th>".format(key) 
        table += "</tr>"

        ipS,tS,press,humS,puANS,puAUSS =[],[] ,[],[],[],[]
        #lichtlist,lichtbuttonlist = [],[]
        for key in keys:
            
            ip,T,p,hum,pupmeAN,pumpeAUS = tabledict[key]
            #lichtlist,lichtbuttonlist = tabledict[key]
            cls.ip = ip
            ipS.append("<td> {}</td>".format(ip))
            tS.append("<td>{}</td>".format(T))
            press.append("<td>{}</td>".format(p))
            humS.append("<td>{}</td>".format(hum))
            puANS.append("<td>{}</td>".format(pupmeAN))
            puAUSS.append("<td>{}</td>".format(pumpeAUS))
            #lichtlist.append("<td>{}</td>".format(licht))
            #lichtbuttonlist.append("<td>{}</td>".format(button))
        
        table += cls.addRow(ipS)
        table += cls.addRow(tS)
        table += cls.addRow(press)
        table += cls.addRow(humS)
        table += cls.addRow(puANS)
        table += cls.addRow(puAUSS)
        #table += cls.addRow(lichtlist)
        #table += cls.addRow(lichtbuttonlist)
        table += "</table>"    
        return table

    @classmethod
    def addRow(cls,liste):
        cls.tabellereihe = "<tr>"
        for i in liste:
            cls.tabellereihe += i
        cls.tabellereihe += "</tr>"
        return cls.tabellereihe

    @classmethod
    def save_new_Wifi (cls,**args): 
        if cls.connect_Wifi(args["ssid"],args["password"]): #wird nicht wahr trotz handy wlan testeingabe
            import json
            config_file = "/http/networks.json"
            with open(config_file,"r") as f:
                config = json.loads(f.read())
            
            config['known_networks'].append({
			"ssid": args["ssid"],
			"password": args["password"],
			"enables_webrepl": False})

            with open(config_file,"w")as f:             #speichern der geänderten var als Json datei
                json.dump(config,f)
            print("Netzwerk aufgenommen: ",args["ssid"])
            return "W-Lan verbunden und gespeichert"
        return "Fehler bei verbinden des W-Lans!"
   
    @classmethod
    def connect_Wifi(cls, ssid, password) -> bool:
        try:
            import network
            wlan = network.WLAN(network.STA_IF)
            wlan.connect(ssid, password)
            for check in range(0, 10): 
                if wlan.isconnected():
                    return True
                sleep(0.5)
        except:
            return False

    @classmethod
    def query_verarbeiten (cls,**parDict):
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