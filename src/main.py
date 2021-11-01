from RedditAPI import RedditAPI


if __name__ == '__main__':
    rAPI = RedditAPI()
    rAPI.subreddit_stream("bitcoin")
