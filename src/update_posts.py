import praw
import json
import requests

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

    def patch_24h_old_posts(self, subreddit):
        r = requests.patch(self.api_url + f"coins/{subreddit}?age=1", params=self.payload)
        data = r.json()
        print(data)


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

up = UpdatePosts()
up.get_24h_old_posts('btc')
