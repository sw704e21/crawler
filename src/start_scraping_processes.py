import csv
from multiprocessing import Process
from RedditAPI import RedditAPI

reddits_to_scrape = []


def start_crawler(reddit_name):
    crawler = RedditAPI()
    crawler.subreddit_stream(reddit_name)


if __name__ == '__main__':
    with open('subreddits.csv', newline='') as f:
        reader = csv.reader(f)
        reddits_to_scrape = list(reader)
    for reddit in reddits_to_scrape:
        p = Process(target=start_crawler, args=(reddit),)
        p.start()
