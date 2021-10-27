from RedditAPI import RedditAPI
import requests


if __name__ == '__main__':
    rAPI = RedditAPI()
    rAPI.subreddit_stream("bitcoin")
