from multiprocess_scraper import MultiProcessScraper
from update_posts import UpdatePosts
from multiprocessing import Process
from PriceAPI import PriceAPI
import logging
import datetime
import os

if __name__ == '__main__':
    now = datetime.datetime.now()
    logging.basicConfig(filename=f"{os.getcwd()}/logs/{now.day}-{now.month}-{now.year}.log", filemode="a",
                        level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    logging.info("Starting crawler")
    manager = MultiProcessScraper()
    updating = UpdatePosts()
    price = PriceAPI()
    manager_process = Process(target=manager.run)
    scheduler_process = Process(target=updating.scheduler)
    price_process = Process(target=price.run)
    manager_process.start()
    scheduler_process.start()
    price_process.start()
