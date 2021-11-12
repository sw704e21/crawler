import praw
import json
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
# import schedule
import os
from typer import Option
from subreddit_downloader import downloader
import typer


def initialize_reddit():
    reddit = praw.Reddit(client_id='y9aowlfsW7dLZyFuyrpH-w',
                         client_secret='3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ',
                         user_agent='Huften')
    return reddit

class UpdatePosts:

    # Specify the wanted fields from praw.submissions to be send through the API
    fields = ('title', 'url', 'selftext', 'score', 'created_utc', 'num_comments')

    def __init__(self):
        self.incoming_submissions = []
        self.outgoing_submissions = []
        self.api_url = "http://cryptoserver.northeurope.cloudapp.azure.com/"
        self.subreddit = ""
        self.id_list = ""
        self.payload = json.dumps(self.incoming_submissions)
        self.run_id = datetime.today().strftime('%Y%m%d%H')

    def download_data(self, subreddit):
        bool = fetching = False
        timecode = 1609459201
        # typer.run(downloader(subreddit=subreddit, output_dir="./data/", batch_size=1, laps=1, reddit_id="y9aowlfsW7dLZyFuyrpH-w", reddit_secret="3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ", reddit_username="Huften", utc_after=1636539342))
        os.system(f"python subreddit_downloader.py {subreddit} --batch-size 2 --laps 2 "
                  f"--reddit-id y9aowlfsW7dLZyFuyrpH-w --reddit-secret 3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ "
                  f"--reddit-username Huften --utc-after {timecode}")

    def update_data(self, data):
        for submission in data:
            to_dict = vars(submission)
            url = submission['url']
            submission_updated = initialize_reddit().submission(url=url)
            submission['score'] = submission_updated.score
            submission['num_comments'] = submission_updated.num_comments
            sub_dict = {field: to_dict[field] for field in self.fields}
            print(sub_dict)
            # print(r)
            # print(self.payload)

    def fetch_data(self):
        f = open('data/Bitcoin/20211111/submissions/0.njson', "r")
        data = json.load(f)
        for i in data['title']:
            print(i)
        f.close()

        # with open("data/Bitcoin/20211111/submissions/0.njson", 'r') as f:


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
    up.download_data("Bitcoin")
    # up.fetch_data()


