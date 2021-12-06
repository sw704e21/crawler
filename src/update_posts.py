import praw
import requests
from datetime import datetime
import schedule
import os
import time
import logging
from post_data import PostData

logger = logging.getLogger("downloader")


# Calculation of x amount of previous days, returned as unix timestamp.
def past_days_unix(days):
    now = datetime.now()
    unix_timestamp = (time.mktime(now.timetuple()))
    daysago = time.localtime(unix_timestamp - (days * 86400))
    return daysago


# Calculation of the past 24 hours, returned as unix timestamp.
def past_24h_unix():
    now = datetime.now()
    unix_timestamp = (time.mktime(now.timetuple()))
    yday = int((unix_timestamp - 86400))
    return yday


# Calculation x amount of previous hours, returned as unix timestamp.
def past_hours_unix(hours):
    now = datetime.now()
    unix_timestamp = (time.mktime(now.timetuple()))
    hour_ago = time.localtime(unix_timestamp - (hours * 3600))
    return hour_ago


def initialize_reddit():
    reddit = praw.Reddit(client_id='y9aowlfsW7dLZyFuyrpH-w',
                         client_secret='3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ',
                         user_agent='Huften')
    return reddit


class UpdatePosts:

    def __init__(self):
        self.api_url = "http://cryptoserver.northeurope.cloudapp.azure.com/coins"

    def get_tracked_subreddits(self):
        r = requests.get(self.api_url + "/all/names")
        data = r.json()
        return data

    def scheduler(self):
        logger.info("Start update scheduler")
        # self.test_schedule()
        self.daily_schedule()
        self.weekly_schedule()
        while True:
            schedule.run_pending()
            time.sleep(1)

    def test_schedule(self):
        coins_list = self.get_tracked_subreddits()
        schedule.every(5).seconds.do(self.update_posts_test, list=coins_list)

    def daily_schedule(self):
        coins_list = self.get_tracked_subreddits()
        schedule.every().hour.at(":30").do(self.update_posts_daily, list=coins_list)

    def weekly_schedule(self):
        coins_list = self.get_tracked_subreddits()
        schedule.every().day.at("12:00").do(self.update_posts_weekly, list=coins_list)

    def update_posts_test(self, list):
        timecode = past_24h_unix()
        for j in list:
            self.download_data(j, timecode, 3, 3)

    # downloading and patching submissions from the past 24 hours.
    def update_posts_daily(self, list):
        logger.info("Patching interactions hourly")
        timecode = past_24h_unix()
        for j in list:
            self.download_data(j, timecode, 512, 4)

    # downloading and patching submissions from the past 7 days.
    def update_posts_weekly(self, list):
        logger.info("Patching interactions daily")
        timecode = past_days_unix(7)
        for j in list:
            self.download_data(j, timecode, 512, 21)

    # Using the subreddit_downloader script
    def download_data(self, subreddit, timecode, batch_size, laps):
        # Specifying the amount of laps so that when fetching the data, the correct amount of files will be read.
        logger.info("Starting download")
        try:
            os.system(f"python3 src/subreddit_downloader.py {subreddit} --batch-size {batch_size} --laps {laps} "
                      f"--reddit-id y9aowlfsW7dLZyFuyrpH-w --reddit-secret 3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ "
                      f"--reddit-username Huften --utc-after {timecode}")
        except Exception as e:
            logger.error(e)

    # Looping through the downloaded submission data and updating num_comments and score for all the submissions.
    def update_data(self, data):
        if data:
            for submission in data:
                submission['permalink'] = submission['full_link']
                url = submission['permalink']
                update_submissions = initialize_reddit().submission(url=url)
                num_comments = update_submissions.num_comments
                score = update_submissions.score
                interactions = int(num_comments) + int(score)
                self.patch_data(url, interactions, submission)

    # Creating a patch request that updates the interactions for coins in the database.
    def patch_data(self, url: str, interactions: int, data):
        payload = {'url': url, 'interactions': interactions}
        logger.info(f"Patching {payload}")
        r = requests.patch(self.api_url + "/", params=payload)
        try:
            r.raise_for_status()
            logger.info(r.status_code)
        except requests.exceptions.HTTPError as e:
            logger.error(e)
            if r.status_code == 404:
                post = PostData()
                post.post_data(data)
