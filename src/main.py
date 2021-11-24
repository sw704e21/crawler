from multiprocess_scraper import MultiProcessScraper
from update_posts import UpdatePosts
from multiprocessing import Process
from PriceAPI import PriceAPI


if __name__ == '__main__':
    manager = MultiProcessScraper()
    updating = UpdatePosts()
    price = PriceAPI()
    manager_process = Process(target=manager.run)
    scheduler_process = Process(target=updating.scheduler)
    price_process = Process(target=price.run)
    manager_process.start()
    scheduler_process.start()
    price_process.start()
