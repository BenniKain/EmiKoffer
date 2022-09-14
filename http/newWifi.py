class NewWifi:
    @classmethod
    def createHTML(cls):
        response = ""
        with open('/HTML_CSS/newWIFI.html', 'r') as f:
            for line in f.readlines():
                response += line                

        available_networks = cls.get_wifis()
        # Sort fields by strongest first in case of multiple SSID access points
        #networktable = cls.listtoHTMl (available_networks)
        networktable = cls.listtoHTMLlistBOX (available_networks)  # max 5 wlanssonst gehts ned
        response = response.format(availableWIFI = networktable)
        #response = response.format()
        return response

    @classmethod
    def get_wifis(cls):
        import network
        available_networks = []
        for wlans in network.WLAN(network.STA_IF).scan():
            ssid = wlans[0].decode("utf-8")
            bssid = wlans[1]
            strength = wlans[3]
            available_networks.append(dict(ssid=ssid, bssid=bssid, strength=strength))
        # Sort fields by strongest first in case of multiple SSID access points
        available_networks.sort(key=lambda station: station["strength"], reverse=True)
        return available_networks
    @classmethod
    def listtoHTMl(cls,liste):
        table ="<table>"
        liste.insert(0,"Name") 
        for k in liste:
            table += "<tr><td>" +str(k)+ "</td></tr>" 
        table += "</table>"    
        return table

    @classmethod
    def listtoHTMLlistBOX(cls,liste):
        table = ""  
        for i in range(5):
            table += '<input type="checkbox" name="ssid" value={}>{}<br>'.format(liste[i]["ssid"],liste[i]["ssid"])
        #print(table)
        return table