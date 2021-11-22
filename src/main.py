from multiprocess_scraper import MultiProcessScraper
from update_posts import UpdatePosts
import multiprocessing
import time


if __name__ == '__main__':
    manager = MultiProcessScraper()
    updating = UpdatePosts()
    manager_process = multiprocessing.Process(target=manager.run)
    scheduler_process = multiprocessing.Process(target=updating.scheduler)
    manager_process.start()
    scheduler_process.start()



