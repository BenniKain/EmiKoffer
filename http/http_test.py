import network
from steuerung.gpfile import Steuerung
from steuerung.methoden import TableErstellen,LedLIcht
from http.newWifi import NewWifi
aufrufe = 0                                         #anzahl aufrufe der Webseite

def qs_parse(qs):
    parameters = {}
    ampersandSplit = qs.split("&")                  #ist zeichen um mehrer ARgs zu concatenaten
    for element in ampersandSplit:
        equalSplit = element.split("=")             #weist den jeweiligen "Wert für das Argument aus
        parameters[equalSplit[0]] = equalSplit[1]   #fügt dict paar zu dictionary hinzu
    return parameters

def get_zaehler(zaehler):
    zaehler += 1
    return zaehler

def get_GET(req):
    try:
        response =""
        getcall = req.decode().split()[1]
        if ".css" in req:  
            datenTyp = "css"
            with open('/HTML_CSS/style.css', 'r') as f:
                response = f.read()
            return datenTyp,response

        elif ".ico" in req:
            datenTyp = "ico"
            return datenTyp,response

        else:
            datenTyp = "html"
            print(req)      #b'GET /?Koffer=Koffer1&ip=192.168.4.1&function=PumpeAN HTTP/1.1\r\n'
            print(getcall)  #/?Koffer=Koffer1&ip=192.168.4.1&function=PumpeAN
            if "/data" in getcall:                          #empfangen von daten
                try:
                    dataDict = qs_parse(getcall.split("?")[1])                #dictionary mit alle esp datensätzen updaten
                    Steuerung.update_Kofferdict(dataDict) #http://192.168.8.100/data?espID=Koffer1&ip=192.168.4.1&temp=5&press=1001&alt=300&tBMP=23&hum=70
                    response = "Update erfolgreich"
                    print(Steuerung.kofferDict)
                except:
                    response ="Dict ERROR"
                finally:
                    return datenTyp, response

            if "/newWIFI" in getcall:
                response = NewWifi.createHTML()
                return datenTyp, response

            else:           #elif "/" == getcall or "/?" in getcall:
                #steuermethoden.read_DHT_data()
                with open('/HTML_CSS/anzeige.html', 'r') as f:
                    for line in f.readlines():
                        response += line                
                table = TableErstellen.get_table(Steuerung.datenDict)
        
        if "?" in getcall:                          #frägt ob eine request mit argumenten ist bstp /data?ID=192.168.0.100&NAME=Koffer
            path = getcall.split("?")[0]
            args = qs_parse(getcall.split("?")[1])  #splitted args in Dictionary
            #print (args)
            if path == "/post":
                command = TableErstellen.save_new_Wifi(**args)
            elif path == "/licht":
                command = LedLIcht.lichtint(**args)
                Steuerung.led.duty(command)
            else:
                command = TableErstellen.query_verarbeiten(**args)
        
        else:
            command=""
        global aufrufe
        aufrufe += 1
        response = response.format(table= table,command= command,aufrufe = str(aufrufe)) 

        return datenTyp,response
    except Exception as e:
        print("Fehler in http.test.py: " ,e)
        raise e

def get_POST(req,cl_file):
    try:
        print("Request",req)
        if "Content-Length: " in req:
            byteAnzahl = int(req[16:-2])
            print(byteAnzahl)
        print("Post request")
        if byteAnzahl > 0:
            getData = cl_file.read(byteAnzahl)                  # datenlänge ist die anzahl an bytes die im body von post enthalten sind
            print(getData)                      #printed den boy von Post
            response= "Daten erfolgreich gelesen"
        else:
            response = "Keine Daten empfangen, Post Body leer"
        return response
    except Exception as e:
        print("Fehler in get_post methode: ", e)
        raise e