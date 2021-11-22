from multiprocess_scraper import MultiProcessScraper
from update_posts import UpdatePosts
from multiprocessing import Process


if __name__ == '__main__':
    manager = MultiProcessScraper()
    updating = UpdatePosts()
    manager_process = Process(target=manager.run)
    scheduler_process = Process(target=updating.scheduler)
    manager_process.start()
    scheduler_process.start()
