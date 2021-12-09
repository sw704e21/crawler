import praw
import requests
from datetime import datetime
import schedule
import time
import logging
from tweepy import Client
from pushshift_py import PushshiftAPI

TWITTER_APP_KEY = "VVHRzSdTp6T35a04AJuqlr3SR"
TWITTER_APP_SECRET = "83MFy2JuE3sbyLhqWtpKV7KoBLQ7EDQgFCWEXVQgNqf44cJaxD"
TWITTER_KEY = "611585498-MgduwddC5tSVylz6CzUTMJKULy8qM6PJsdASvTtX"
TWITTER_SECRET = "S7gX7cTaqfnfkenpG0C3PD0Fu0YGAMKEijgGsWmsE1OZV"
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAALHPVAEAAAAAfHjUBIowk4cFZCHjN42zfoYoxKo%3D3gqjnwkNbYKL9ek5NsvoMAVu6aClSjy" \
                       "xl6PxWFVXOgkLBnM9xN"

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
        self.api_url = "http://cryptoserver.northeurope.cloudapp.azure.com"

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
        schedule.every(5).seconds.do(self.update_posts_test)

    def daily_schedule(self):
        schedule.every().hour.at(":30").do(self.update_posts_daily)

    def weekly_schedule(self):
        schedule.every().day.at("12:00").do(self.update_posts_weekly)

    def update_posts_test(self):
        self.download_data(0.5)

    # downloading and patching submissions from the past 24 hours.
    def update_posts_daily(self):
        logger.info("Patching interactions hourly")
        self.download_data(1)

    # downloading and patching submissions from the past 7 days.
    def update_posts_weekly(self):
        logger.info("Patching interactions daily")
        self.download_data(7)

    def download_data(self, timecode):
        param = {'age': timecode}
        r = requests.get(self.api_url + '/sentiment/ids/reddit', params=param)
        lst = r.json()
        i = 100
        j = 0
        a = PushshiftAPI()
        while j * i < len(lst):
            slice = lst[i * j: i * (j + 1)]
            self.update_data(a.search_submissions(ids=slice, limit=i))
            j += 1
        r = requests.get(self.api_url + '/sentiment/ids/twitter', params=param)
        lst = r.json()
        i = 100
        j = 0
        a = Client(TWITTER_BEARER_TOKEN, TWITTER_APP_KEY, TWITTER_APP_SECRET, TWITTER_KEY, TWITTER_SECRET)
        while j * i < len(lst):
            slice = lst[i * j: i * (j + 1)]
            lst = a.get_tweets(ids=slice, tweet_fields='public_metrics').data
            for tweet in lst:
                self.patch_data(str(tweet.id), tweet.public_metrics['reply_count'] + tweet.public_metrics['like_count'])
            j += 1

    # Using the subreddit_downloader script
    # def download_data(self, subreddit, timecode, batch_size, laps):
    #    # Specifying the amount of laps so that when fetching the data, the correct amount of files will be read.
    #    logger.info("Starting download")
    #    try:
    #        os.system(f"python3 src/subreddit_downloader.py {subreddit} --batch-size {batch_size} --laps {laps} "
    #                  f"--reddit-id y9aowlfsW7dLZyFuyrpH-w --reddit-secret 3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ "
    #                  f"--reddit-username Huften --utc-after {timecode}")
    #    except Exception as e:
    #        logger.error(e)

    # Looping through the downloaded submission data and updating num_comments and score for all the submissions.
    def update_data(self, data):
        if data:
            for submission in data:
                uuid = submission.id
                num_comments = submission.num_comments
                score = submission.score
                interactions = int(num_comments) + int(score)
                self.patch_data(uuid, interactions)

    # Creating a patch request that updates the interactions for coins in the database.
    def patch_data(self, uuid: str, interactions: int):
        payload = {'uuid': uuid, 'interactions': interactions}
        logger.info(f"Patching {payload}")
        r = requests.patch(self.api_url + "/coins", params=payload)
        try:
            r.raise_for_status()
            logger.info(r.status_code)
        except requests.exceptions.HTTPError as e:
            logger.error(e)
