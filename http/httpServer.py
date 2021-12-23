from http.http_test import get_GET, get_POST
import socket
import uasyncio as asyncio
from steuerung.gpfile import Steuerung 

#import machine

class HttpServer():
    @classmethod
    def get_Steuerung(cls):
        Steuerung.setup()
        pass
    @classmethod
    def start_Server(cls):
        cls.get_Steuerung()
        cls.addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        cls.s = socket.socket()
        cls.s.bind(cls.addr)
        cls.s.listen(1)
        print('listening on', cls.addr)
        cls.listening()

        #loop = asyncio.get_event_loop()
        #loop.create_task(cls.s.accept()) # Schedule ASAP

    @classmethod
    def listening(cls):
        while True:  
            #print(machine.Pin(13).value()) #wird nur bei httpreq aufgerufen       
            try:
                cl, addr = cls.s.accept()   #accept wartet und blockiert ddurch asyncio, non blocking mehtod needed
                print('client connected from', addr)
                cl_file = cl.makefile('rwb', 0)
                ico,css= False,False
                getReq = []
                while True:
                    reqline =cl_file.readline()
                    getReq.append(reqline)             #wenn nicht alle zeilen gelesen funktionierts nicht
                    #print(getReq)
                    if not reqline or reqline == b'\r\n':
                        break

                if "GET" in getReq[0]:
                    respType, response = get_GET(getReq[0]) #b'GET /?Koffer=Koffer1&ip=192.168.4.1&function=PumpeAN HTTP/1.1\r\n'
                    reqtype ="GET"          #respType kann css datei sein oder html oder .ico bilder oder so etwas    
                elif "POST" in getReq[0]: #b'POST /de?espID=Koffer2&ip=192.168.4.1&function=PumpeAUS HTTP/1.1\r\n'
                    reqtype ="POST"
                    datenlänge = get_POST(getReq[3]) #z.b. b'Content-Length: 24\r\n'
                
                print("Sending Response")
                if reqtype == "POST":
                    print("Post request")
                    if datenlänge > 0:
                        getData = cl_file.read(datenlänge)                  # datenlänge ist die anzahl an bytes die im body von post enthalten sind
                        print(getData)                      #printed den boy von Post
                        response= "Daten erfolgreich gelesen"
                    else:
                        response = "Keine Daten empfangen, Post Body leer"
                    cl.send('HTTP/1.0 200 OK\r\n\r\n')                          # muss keine response geben denke ich da daten zum server gepusht werden
                    cl.send(response)        

                if reqtype == "GET":
                    print(response[:30])
                    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/{}\r\n\r\n'.format(respType))
                    cl.send(response)
                
                print("Response sent")
                cl.close()
            except Exception as e:
                print("Fehler beim Verbinden des Client!. {}".format(e))
                raise
                #cls.addr.shutdown(socket.SHUT_RDWR)
if __name__ == "__main__":
    HttpServer.start_Server()

