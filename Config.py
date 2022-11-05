import yaml
import os

class Config:
    def __init__(self) -> None:
        with open("config.yaml", "r",  encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.username = os.environ.get('RIOT_USERNAME')
            self.password = os.environ.get('RIOT_PASSWORD')
            self.debug = os.environ.get('DEBUG', config.get("debug", False))

        with open("bestStreams.txt", "r",  encoding='utf-8') as f:
            self.bestStreams = f.read().splitlines()
        