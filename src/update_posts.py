import praw
import json
import requests


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

    def get_24h_old_posts(self, subreddit):
        r = requests.get(self.api_url + f"coins/{subreddit}?age=1", params=self.payload)
        print(r)
        print(self.payload)
up = UpdatePosts()
up.get_24h_old_posts('bitcoin')
