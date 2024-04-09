import os
from dataclasses import dataclass
from typing import List

import yaml
from dotenv import load_dotenv
import logging


load_dotenv()


@dataclass
class Source:
    NAME: str
    NUMBER: str


@dataclass
class Config:
    ACCESS_TOKEN: str
    SOURCES: List[Source]


with open('//home//mister228orange//mysite//config.yaml', 'r') as file:
    config_data = yaml.safe_load(file)


logging.error(config_data)
access_token = config_data.get('ACCESS_TOKEN', '')
sources_data = config_data.get('SOURCES', [])
sources = [Source(NAME=source.get('name', ''), NUMBER=str(source.get('number', ''))) for source in sources_data]
logging.error(sources)

cfg = Config(ACCESS_TOKEN=access_token, SOURCES=sources)
