import praw
import json
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import schedule
import os
from typer import Option
import typer
import time
import datetime
import shutil


def initialize_reddit():
    reddit = praw.Reddit(client_id='y9aowlfsW7dLZyFuyrpH-w',
                         client_secret='3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ',
                         user_agent='Huften')
    return reddit

class UpdatePosts:

    def __init__(self):
        self.api_url = "http://cryptoserver.northeurope.cloudapp.azure.com/coins"
        self.laps = 0

    def get_tracked_subreddits(self):
        list = []
        r = requests.get(self.api_url + "/all")
        data = r.json()
        for coin in data:
               list.append(coin['name'])
        return list

    def scheduler(self):
        self.test_schedule()
        while True:
            schedule.run_pending()
            time.sleep(1)

    def test_schedule(self):
        coins_list = self.get_tracked_subreddits()
        schedule.every(5).minutes.do(self.update_posts_test(coins_list))

    def daily_schedule(self):
        coins_list = self.get_tracked_subreddits()
        # schedule.every().day.at("00:00").do(self.update_posts_daily(coins_list))

    def weekly_schedule(self):
        coins_list = self.get_tracked_subreddits()
        # schedule.every().monday.do(self.update_posts_weekly(coins_list))

    def update_posts_test(self, list):
        timecode = self.past_24h_unix()
        timeago = self.past_24h()
        for j in list:
            self.download_data(j, timecode, timeago, 3, 3)
            self.update_data(timeago, j)
        self.delete_data()

    # downloading and patching submissions from the past 24 hours.
    def update_posts_daily(self, list):
        timecode = self.past_24h_unix()
        timeago = self.past_24h()
        for j in list:
            self.download_data(j, timecode, timeago, 512, 3)
            self.update_data(timeago, j)
        self.delete_data()

    # downloading and patching submissions from the past 7 days.
    def update_posts_weekly(self, list):
        timecode = self.past_days_unix(7)
        timeago = self.past_days(7)
        for j in list:
            self.download_data(j, timecode, timeago, 512, 21)

            self.update_data(timeago, j)
        self.delete_data()

    # Using the subreddit_downloader script
    def download_data(self, subreddit, timecode, timeago, batch_size, laps):

        # Specifying the amount of laps so that when fetching the data, the correct amount of files will be read.
        self.laps = laps

        os.system(f"python subreddit_downloader.py {subreddit} --batch-size {batch_size} --laps {laps} "
                  f"--reddit-id y9aowlfsW7dLZyFuyrpH-w --reddit-secret 3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ "
                  f"--reddit-username Huften --utc-after {timecode} --run-id {timeago}")

    # Looping through the downloaded submission data and updating num_comments and score for all the submissions.
    def update_data(self, id, subreddit):
        data = self.fetch_data(id, subreddit)
        for submission in data:
            url = submission['full_link']
            update_submissions = initialize_reddit().submission(url=url)
            num_comments = update_submissions.num_comments
            score = update_submissions.score
            interactions = int(num_comments) + int(score)
            self.patch_data(url, interactions)

    # Creating a patch request that updates the interactions for coins in the database.
    def patch_data(self, url: str, interactions: int):
        payload = {'url': url, 'interactions': interactions}
        r = requests.patch(self.api_url, params=payload)
        try:
            r.raise_for_status()
            print(r)
        except requests.exceptions.HTTPError as e:
            print(e)

    # Looping through the files containing the submission bodies.
    def fetch_data(self, id, subreddit):
        data_final = []
        for i in range(self.laps):
           try:
               f = open(f'data/{subreddit}/{id}/submissions/{i}.njson', "r")
               data = json.load(f)
               f.close()
               data_final.extend(data)
           except IOError as e:
               print('Operation failed: %s' % e.strerror)

        return data_final

    # Delete the data directory for all its contents.
    def delete_data(self):
        shutil.rmtree('data')

    # Calculation of x amount of previous days, returned as unix timestamp.
    def past_days_unix(self, days):
        now = datetime.datetime.now()
        unix_timestamp = (time.mktime(now.timetuple()))
        yday = time.localtime(unix_timestamp - (days * 86400))

        return yday

    # Calculation of the past 24 hours, returned as unix timestamp.
    def past_24h_unix(self):
        now = datetime.datetime.now()
        unix_timestamp = (time.mktime(now.timetuple()))
        yday = int((unix_timestamp - 86400))
        return yday

    # Calculation x amount of previous hours, returned as unix timestamp.
    def past_hours_unix(self, hours):
        now = datetime.datetime.now()
        unix_timestamp = (time.mktime(now.timetuple()))
        hour_ago = time.localtime(unix_timestamp - (hours * 3600))

        return hour_ago

    # Calculation x amount of previous days, returned weekday-day-month-year-hour-minute + PM/AM.
    def past_days(self, days):
        date = datetime.datetime.now() - datetime.timedelta(days=days)

        return date.strftime("%A-%d-%B-%Y-%I-%M%p")

    # Calculation of the previous 24 hours, returned weekday-day-month-year-hour-minute + PM/AM.
    def past_24h(self):
        date = datetime.datetime.now() - datetime.timedelta(days=1)

        return date.strftime("%A-%d-%B-%Y-%I-%M%p")

    # Calculation x amount of previous hours, returned weekday-day-month-year-hour-minute + PM/AM.
    def past_hours(self, hours):
        date = datetime.datetime.now() - datetime.timedelta(hours=hours)

        return date.strftime("%A-%d-%B-%Y-%I-%M%p")

if __name__ == "__main__":

    up = UpdatePosts()
    # up.update_posts_daily(["shibainucoin", "dogelon", "etherum", "dogecoin", "bitcoin"])
    # up.get_tracked_subreddits()
    up.test_schedule()



