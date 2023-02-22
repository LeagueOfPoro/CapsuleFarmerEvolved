import yaml, requests
from yaml.parser import ParserError
from rich import print
from pathlib import Path

from Exceptions.InvalidCredentialsException import InvalidCredentialsException


class Config:
    """
    A class that loads and stores the configuration
    """

    REMOTE_BEST_STREAMS_URL = "https://raw.githubusercontent.com/LeagueOfPoro/CapsuleFarmerEvolved/master/config/bestStreams.txt"
    RIOT_API_KEY = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"

    def __init__(self, configPath: str) -> None:
        """
        Loads the configuration file into the Config object

        :param configPath: string, path to the configuration file
        """
        
        self.accounts = {}
        try:
            configPath = self.__findConfig(configPath)
            with open(configPath, "r", encoding='utf-8') as f:
                config = yaml.safe_load(f)
                accs = config.get("accounts")
                for account in accs:
                     if "username" != accs[account]["username"]:
                        self.accounts[account] = {
                        #Orig data
                        "username": accs[account]["username"],
                        "password": accs[account]["password"],
                        
                        #IMAP data
                        "imapUsername": accs[account].get("imapUsername", ""),
                        "imapPassword": accs[account].get("imapPassword", ""),
                        "imapServer": accs[account].get("imapServer", ""),
                        }
                if not self.accounts:
                    raise InvalidCredentialsException                    
                self.debug = config.get("debug", False)
                self.connectorDrops = config.get("connectorDropsUrl", "")
                self.showHistoricalDrops = config.get("showHistoricalDrops", True)
        except FileNotFoundError as ex:
            print(f"[red]CRITICAL ERROR: The configuration file cannot be found at {configPath}\nHave you extacted the ZIP archive and edited the configuration file?")
            print("Press any key to exit...")
            input()
            raise ex
        except (ParserError, KeyError) as ex:
            print(f"[red]CRITICAL ERROR: The configuration file does not have a valid format.\nPlease, check it for extra spaces and other characters.\nAlternatively, use confighelper.html to generate a new one.")
            print("Press any key to exit...")
            input()
            raise ex
        except InvalidCredentialsException as ex:
            print(f"[red]CRITICAL ERROR: There are only default credentials in the configuration file.\nYou need to add you Riot account login to config.yaml to receive drops.")
            print("Press any key to exit...")
            input()
            raise ex
        try:
            remoteBestStreamsFile = requests.get(self.REMOTE_BEST_STREAMS_URL)
            if remoteBestStreamsFile.status_code == 200:
                self.bestStreams = remoteBestStreamsFile.text.split()
        except Exception as ex:
            print(f"[red]CRITICAL ERROR: Beststreams couldn't be loaded. Are you connected to the internet?")
            print("Press any key to exit...")
            input()
            raise ex

    def getAccount(self, account: str) -> dict:
        """
        Get account information

        :param account: string, name of the account
        :return: dictionary, account information
        """
        return self.accounts[account]
    
    def __findConfig(self, configPath):
        """
        Try to find configuartion file in alternative locations.

        :param configPath: user suplied configuartion file path
        :return: pathlib.Path, path to the configuration file
        """
        configPath = Path(configPath)
        if configPath.exists():
            return configPath
        if Path("../config/config.yaml").exists():
            return Path("../config/config.yaml")
        if Path("config/config.yaml").exists():
            return Path("config/config.yaml")
        
        return configPath
