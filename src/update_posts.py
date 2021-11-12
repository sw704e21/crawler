import praw
import json
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
# import schedule
import os
from typer import Option
import typer
import time
import datetime


def initialize_reddit():
    reddit = praw.Reddit(client_id='y9aowlfsW7dLZyFuyrpH-w',
                         client_secret='3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ',
                         user_agent='Huften')
    return reddit

class UpdatePosts:

    # Specify the wanted fields from praw.submissions to be send through the API
    fields = ('title', 'full_link', 'selftext', 'score', 'created_utc', 'num_comments')

    def __init__(self):
        self.incoming_submissions = []
        self.outgoing_submissions = []
        self.api_url = "http://cryptoserver.northeurope.cloudapp.azure.com/"
        self.subreddit = ""
        self.id_list = ""
        self.payload = json.dumps(self.incoming_submissions)
        self.fetching = False
        self.run_id = ""
        self.laps = 0

    def update_posts_daily(self, list):
        timecode = self.past_24h_unix()
        timeago = self.past_24h()
        self.laps = 3
        for j in list:
            self.download_data(j, timecode, timeago, 3, 3)

            self.update_data(timeago, j)



    def download_data(self, subreddit, timecode, timeago, batch_size, laps):
        self.run_id = timeago
        self.laps = laps

        # typer.run(downloader(subreddit=subreddit, output_dir="./data/", batch_size=1, laps=1, reddit_id="y9aowlfsW7dLZyFuyrpH-w", reddit_secret="3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ", reddit_username="Huften", utc_after=1636539342))
        os.system(f"python subreddit_downloader.py {subreddit} --batch-size {batch_size} --laps {laps} "
                  f"--reddit-id y9aowlfsW7dLZyFuyrpH-w --reddit-secret 3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ "
                  f"--reddit-username Huften --utc-after {timecode} --run-id {timeago}")

    def update_data(self, id, subreddit):
        data = self.fetch_data(id, subreddit)
        self.run_id = datetime.datetime.today().strftime('%Y%m%d%H')
        for submission in data:
            url = submission['full_link']
            num_comments = submission['num_comments']
            score = submission['score']
            interactions = int(num_comments) + int(score)
            patch_data(submission_updated, interactions, url)

    def patch_data(self, url, interactions):
        payload = {'url': url, 'interactions': interactions}
        r = requests.patch(api_url, params=payload)
        try:
            r.raise_for_status()
            print(r)
        except requests.exceptions.HTTPError as e:
            print(e)

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

    def fetch_dataKEK(self):
        f = open('data/Bitcoin/20211112/submissions/0.njson', "r")
        data = json.load(f)
        print(data)
        f.close()
        return data

    def past_days_unix(self, days):
        now = datetime.datetime.now()
        unix_timestamp = (time.mktime(now.timetuple()))
        yday = time.localtime(unix_timestamp - (days * 86400))

        return yday

    def past_24h_unix(self):
        now = datetime.datetime.now()
        unix_timestamp = (time.mktime(now.timetuple()))
        yday = int((unix_timestamp - 86400))
        return yday

    def past_hours_unix(self, hours):
        now = datetime.datetime.now()
        unix_timestamp = (time.mktime(now.timetuple()))
        hour_ago = time.localtime(unix_timestamp - (hours * 3600))

        return hour_ago

    def past_days(self, days):
        return datetime.datetime.now() - datetime.timedelta(days=days)

    def past_24h(self):
        date = datetime.datetime.now() - datetime.timedelta(days=1)

        return date.strftime("%A-%d-%B-%Y-%I:%M%p")

    def past_hours(self, hours):
        return datetime.datetime.now() - datetime.timedelta(hours=hours)


    '''
    def add_day(self, today):
        today_utc = today.astimezone(datetime.timezone.utc)
        tz = today.tzinfo
        tomorrow_utc = today_utc + datetime.timedelta(days=1)
        tomorrow_utc_tz = tomorrow_utc.astimezone(tz)
        return tomorrow_utc_tz
    '''

if __name__ == "__main__":

    up = UpdatePosts()
    # up.download_data("Bitcoin")
    # up.update_data()
    # up.past_24h()
    up.update_posts_daily(["shibainucoin", "dogelon", "etherum", "dogecoin", "bitcoin"])
    # up.past_24h_unix()


