from http.http_test import get_GET, get_POST
import socket
import uasyncio as asyncio
from steuerung.gpfile import Steuerung 

#import machine

class HttpServer():
    @classmethod
    def start_Server(cls):
        print("Starte http Server")
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
            try:
                cl, addr = cls.s.accept()   #accept wartet und blockiert ddurch asyncio, non blocking mehtod needed
                print('client connected from', addr)
                cl_file = cl.makefile('rwb', 0)
                getReq = []
                while True:
                    reqline =cl_file.readline()
                    getReq.append(reqline)             #wenn nicht alle zeilen gelesen funktionierts nicht
                    if not reqline or reqline == b'\r\n':
                        break
                
                print(getReq)

                if "POST" in getReq[0]: #b'POST /de?espID=Koffer2&ip=192.168.4.1&function=PumpeAUS HTTP/1.1\r\n'
                    response = get_POST(getReq[3],cl_file) #z.b. b'Content-Length: 24\r\n'
                    cl.send('HTTP/1.0 200 OK\r\n\r\n') # muss keine response geben denke ich da daten zum server gepusht werden
                    cl.send(response) 

                elif "GET" in getReq[0]:
                    respType, response = get_GET(getReq[0]) #b'GET /?Koffer=Koffer1&ip=192.168.4.1&function=PumpeAN HTTP/1.1\r\n'
                    print(response)
                    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/{}\r\n\r\n'.format(respType))
                    cl.send(response)

                print("Response sent")
                cl.close()
            except Exception as e:
                print("Fehler beim Verbinden des Client!. {}".format(e))
                raise e
                #cls.addr.shutdown(socket.SHUT_RDWR)

if __name__ == "__main__":
    HttpServer.start_Server()

