import yaml


class Config:
    """
    A class that loads and stores the configuration
    """

    def __init__(self, configPath: str) -> None:
        """
        Loads the configuration file into the Config object

        :param configPath: string, path to the configuration file
        """
        
        self.accounts = {}
        try:
            with open(configPath, "r",  encoding='utf-8') as f:
                config = yaml.safe_load(f)
                accs = config.get("accounts")
                for account in accs:
                    self.accounts[account] = {
                        "username": accs[account]["username"],
                        "password": accs[account]["password"],

                    }
                self.debug = config.get("debug", False)
                self.connectorDrops = config.get("connectorDropsUrl", "")
        except FileNotFoundError as ex:
            print(f"ERROR: The configuration file cannot be found at {configPath}")
            raise ex
            
        with open("bestStreams.txt", "r",  encoding='utf-8') as f:
            self.bestStreams = f.read().splitlines()

    def getAccount(self, account: str) -> dict:
        """
        Get account information

        :param account: string, name of the account
        :return: dictionary, account information
        """
        return self.accounts[account]
