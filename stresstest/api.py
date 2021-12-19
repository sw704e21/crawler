from locust import HttpUser, task, between
import random

sort = [
    "mentions",
    "-mentions",
    "-mostInteractions",
    "mostInteractions",
    "relSentiment",
    "-relSentiment",
    "relMentions",
    "-relMentions",
    "displayName",
    "-displayName",
    "price",
    "-price",
    "final_score",
    "-final_score"
]

coins = [
    "ETH",
    "BTC",
    "BAN",
    "SOL",
    "LINK",
    "UNI",
    "ADA",
    "TRX",
    "MATIC",
    "DAI",
    "LTC",
    "SHIB",
    "ALGO",
    "DOGE",
    "DOT",
    "VET",
    "ELON"
]


class CryptoUser(HttpUser):
    wait_time = between(15, 30)

    @task(2)
    def all_coin(self):
        sort_param = random.choice(sort)
        self.client.get(f'/coins/all/?sortParam={sort_param}', name="/coins/all")

    @task
    def coin_info(self):
        coin = random.choice(coins)
        self.client.get(f'/coins/{coin}/info', name="/coins/info")
