import praw
import requests
import time
import logging
logger = logging.getLogger("crawler")


def initialize_reddit():
    reddit = praw.Reddit(client_id='y9aowlfsW7dLZyFuyrpH-w',
                         client_secret='3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ',
                         user_agent='Huften')
    return reddit


class RedditAPI:
    # Specify the wanted fields from praw.submissions to be send through the API
    fields = ('title', 'permalink', 'selftext', 'score', 'created_utc', 'num_comments')

    def __init__(self):
        self.headline = set()
        self.submissions = set()
        self.list_of_items = []
        self.seen_submissions = set()
        self.api_url = "http://cryptoserver.northeurope.cloudapp.azure.com/"

    def subreddit_stream(self, tags):

        reddit_url = "https://www.reddit.com"
        reddit = initialize_reddit()
        query = tags[0]
        for t in tags[1:]:
            query += " OR " + t
        while True:
            try:
                for submission in reddit.subreddit('all').search(query, sort='new', limit=100):
                    # Adding the specified submission fields to the json object
                    to_dict = vars(submission)
                    redditor = to_dict['author']
                    sub_dict = {field: to_dict[field] for field in self.fields}
                    sub_dict['karma'] = redditor.link_karma + redditor.comment_karma
                    sub_dict['created_utc'] *= 1000
                    # sub_dict['source'] = subreddit.display_name
                    sub_dict['permalink'] = reddit_url + sub_dict['permalink']
                    # posting submission data through the API
                    s = self.post_data(sub_dict)
                    if s == 403:
                        break
                time.sleep(1)
            except Exception as e:
                logger.error(e)

    def post_data(self, data):
        logger.info(f"Post sub {data['permalink']}")
        r = requests.post(self.api_url + "data", data=data)

        # Exception handling
        try:
            r.raise_for_status()
            logger.info(r)
        except requests.exceptions.HTTPError as e:
            logger.error(e)
        finally:
            return r.status_code
