import praw
import json
import requests


def initialize_reddit():
    reddit = praw.Reddit(client_id='y9aowlfsW7dLZyFuyrpH-w',
                     client_secret='3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ',
                     user_agent='Huften')
    return reddit


class RedditAPI:

    fields = ('title', 'url', 'selftext', 'score', 'created_utc', 'num_comments')

    def __init__(self):
        self.headline = set()
        self.submissions = set()
        self.list_of_items = []
        self.seen_submissions = set()
        self.fields
        self.api_url = ""

    def subreddit_stream(self, subreddit):

        subreddit = initialize_reddit().subreddit(subreddit)

        for submission in subreddit.stream.submissions():

            self.submissions.add(submission)
            to_dict = vars(submission)
            sub_dict = {field: to_dict[field] for field in self.fields}
            self.list_of_items.append(sub_dict)

            json_str = json.dumps(self.list_of_items)

            with open('data.json', 'w') as f:
                json.dump(self.list_of_items, f)

    def post_data(self):
        f = open('data.json')
        reddit = json.load(f)
        r = requests.post(self.api_url + "data/reddit", data=reddit)

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
