from multiprocess_scraper import MultiProcessScraper
from update_posts import UpdatePosts
from multiprocessing import Process
from PriceAPI import PriceAPI
import logging
import datetime
import os
LEVEL = 'PRODUCTION'
# LEVEL = 'DEVELOPMENT'

logger = logging.getLogger("crawler")
downloader_logger = logging.getLogger("downloader")
logger.setLevel(logging.DEBUG)
downloader_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(name)s:%(levelname)s - %(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

now = datetime.datetime.now()

if LEVEL == 'PRODUCTION':
    handler = logging.FileHandler(f"{os.getcwd()}/logs/{now.day}-{now.month}-{now.year}.log", "a")
elif LEVEL == 'DEVELOPMENT':
    handler = logging.StreamHandler()
else:
    handler = None

handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)
downloader_logger.addHandler(handler)

if __name__ == '__main__':
    logger.info("Starting crawler")
    manager = MultiProcessScraper()
    updating = UpdatePosts()
    price = PriceAPI()
    manager_process = Process(target=manager.run)
    scheduler_process = Process(target=updating.scheduler)
    price_process = Process(target=price.run)
    manager_process.start()
    scheduler_process.start()
    price_process.start()
