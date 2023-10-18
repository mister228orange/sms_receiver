import os


class Config:

    def __init__(self):
        self.ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')


cfg = Config()
