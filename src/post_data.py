import requests
import logging


class PostData:
    fields = ('title', 'url', 'selftext', 'score', 'created_utc', 'num_comments')

    def __init__(self):
        self.api_url = "http://cryptoserver.northeurope.cloudapp.azure.com/"

    def submission_handler(self, filepath: str):
        with open(filepath, 'r') as f:
            data = f.read()
            for submission in data:
                to_dict = vars(submission)
                sub_dict = {field: to_dict[field] for field in self.fields}
                sub_dict['created_utc'] *= 1000
                # posting submission data through the API
                self.post_data(sub_dict)

    def post_data(self, data):
        r = requests.post(self.api_url + "data", data=data)

        # Exception handling
        try:
            r.raise_for_status()
            logging.info(r)
        except requests.exceptions.HTTPError as e:
            logging.error(e)


p = PostData()
p.submission_handler(filepath='...')
