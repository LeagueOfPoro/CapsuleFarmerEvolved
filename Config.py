import yaml


class Config:
    """
    A class that loads and stores the configuration
    """

    def __init__(self) -> None:
        """
        Loads the configuration file into the Config object
        """
        self.accounts = {}
        with open("config.yaml", "r",  encoding='utf-8') as f:
            config = yaml.safe_load(f)
            accs = config.get("accounts")
            for account in accs:
                self.accounts[account] = {
                    "username": accs[account]["username"],
                    "password": accs[account]["password"],

                }
            self.debug = config.get("debug", False)
        with open("bestStreams.txt", "r",  encoding='utf-8') as f:
            self.bestStreams = f.read().splitlines()

    def getAccount(self, account: str) -> dict:
        """
        Get account information

        :param account: string, name of the account
        :return: dictionary, account information
        """
        return self.accounts[account]
