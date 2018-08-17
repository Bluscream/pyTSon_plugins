from requests import request
from bs4 import BeautifulSoup

class TS3CloudProxy(object):
    url = "https://www.ts3.cloud/ts3proxy"
    payload = "input={host}:{port}&proxy="
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        'Accept-Language': "en-US,en;q=0.5",
        'Referer': "https://www.ts3.cloud/ts3proxy",
        'Content-Type': "application/x-www-form-urlencoded",
        # 'Cookie': "__cfduid=d9a56f318887128c83fd88624c51ac2e81523827796; cb-enabled=enabled; _ga=GA1.2.1089033589.1529735502",
        'DNT': "1",
        'Pragma': "no-cache",
        'Cache-Control': "no-cache"
    }
    def generateProxy(self, host, port=9987):
        print("data:", self.payload.format(host=host,port=port))
        response = request("POST", self.url, data=self.payload.format(host=host,port=port), headers=self.headers, verify=False)
        page = response.content
        soup = BeautifulSoup(page, features="html.parser")
        div_alert = soup.find("div", {"class": "alert alert-success alert-dismissable"})
        proxy_adress = div_alert.find("center").find("b").text
        proxy_adress = proxy_adress.split(":")
        proxy = (proxy_adress[0], int(proxy_adress[1]))
        return proxy

