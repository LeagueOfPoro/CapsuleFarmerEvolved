import yaml

class Config:
    def __init__(self) -> None:
        self.accounts = {}
        with open("config.yaml", "r",  encoding='utf-8') as f:
            config = yaml.safe_load(f)
            for account in config:
                self.accounts[account] = {
                    "username": config[account]["username"],
                    "password": config[account]["password"],
                    "debug": config[account].get("debug", False)
                }

        with open("bestStreams.txt", "r",  encoding='utf-8') as f:
            self.bestStreams = f.read().splitlines()

    def getAccount(self, account):
        return self.accounts[account]
        