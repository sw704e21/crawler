from multiprocess_scraper import MultiProcessScraper
from update_posts import UpdatePosts


if __name__ == '__main__':
    manager = MultiProcessScraper()
    manager.run()

    updating = UpdatePosts()
    updating.scheduler()
