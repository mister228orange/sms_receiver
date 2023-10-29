from dataclasses import dataclass
from environs import Env

#import os

@dataclass
class Config:
    ACCESS_TOKEN: str



# os.environ.get('ACCESS_TOKEN', 'hard_coded_token')

env = Env()
env.read_env()


cfg = Config(ACCESS_TOKEN=env("ACCESS_TOKEN"))
