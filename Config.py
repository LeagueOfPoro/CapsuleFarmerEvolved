import yaml

class Config:
    def __init__(self) -> None:
        with open("config.yaml", "r",  encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.username = config["username"]
            self.password = config["password"]

        with open("bestStreams.txt", "r",  encoding='utf-8') as f:
            self.bestStreams = f.read().splitlines()
        