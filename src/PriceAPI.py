import requests
import schedule
import time


class PriceAPI:
    def __init__(self):
        self.cryptoAPI = "http://cryptoserver.northeurope.cloudapp.azure.com"
        self.priceAPI = "https://api.livecoinwatch.com"
        self.apikey = "dfb9d16f-b1ed-41cc-ab52-1a2384dfd566"
        self.tracking = []
        self.get_identifiers()

    def run(self):
        print(self.tracking)

        schedule.every().hour.do(self.price_hour)
        schedule.every().minute.do(self.price_minutes)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def get_identifiers(self):
        self.tracking = []
        tracks = requests.get(self.cryptoAPI + "/track")
        for t in tracks.json():
            self.tracking.append(t['identifier'])

    def price_minutes(self):
        prices = self.get_prices()
        for p in prices.keys():
            res = requests.patch(self.cryptoAPI + "/price/" + p + "/" + str(prices[p]))
            print(res)

    def price_hour(self):
        print("Posting")
        self.get_identifiers()
        prices = self.get_prices()
        for p in prices.keys():
            body = {'identifier': p, 'price': prices[p]}
            res = requests.post(self.cryptoAPI + '/price', json=body)
            print(res)


    def get_prices(self):
        headers = {'content-type': 'application/json', 'x-api-key': self.apikey}
        body = {"currency": 'USD', "sort": 'rank', "order": 'ascending', "offset": 0, "limit": 200, "meta": False}
        price_list = requests.post(self.priceAPI + "/coins/list", headers=headers, json=body).json()
        prices = {}
        for p in price_list:
            if p['code'] in self.tracking:
                prices[p['code']] = p['rate']
        for id in self.tracking:
            if id not in prices.keys():
                body = {"currency": 'USD', "code": id, "meta": True}
                price = requests.post(self.priceAPI + "/coins/single", headers=headers, json=body).json()
                prices[id] = price['rate'] if price['rate'] is not None else 0
        return prices
