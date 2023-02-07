import yaml
from yaml.parser import ParserError
from rich import print
from pathlib import Path

from Exceptions.InvalidCredentialsException import InvalidCredentialsException


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
            configPath = self.__findConfig(configPath)
            with open(configPath, "r",  encoding='utf-8') as f:
                config = yaml.safe_load(f)
                accs = config.get("accounts")
                onlyDefaultUsername = True
                for account in accs:
                    self.accounts[account] = {
                        "username": accs[account]["username"],
                        "password": accs[account]["password"],

                    }
                    if "username" != accs[account]["username"]:
                        onlyDefaultUsername = False
                if onlyDefaultUsername:
                    raise InvalidCredentialsException     
                self.dropNotification = config.get("dropNotification", False)
                self.Notification_2FA = config.get("2FANotification", False)               
                self.debug = config.get("debug", False)
                self.connectorDrops = config.get("connectorDropsUrl", "")
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
            
        with open("bestStreams.txt", "r",  encoding='utf-8') as f:
            self.bestStreams = f.read().splitlines()

    def getAccount(self, account: str) -> dict:
        """
        Get account information

        :param account: string, name of the account
        :return: dictionary, account information
        """
        return self.accounts[account]
    
    def getDropNotification(self) -> bool:
        """
        Get Drop notification flag

        :return: boolean, Drop notification flag
        """
        return self.dropNotification
    
    def get2FANotification(self) -> bool:
        """
        Get 2FA notification flag

        :return: boolean, 2FA notification flag
        """
        return self.Notification_2FA
    
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
            print(f"[red]ERROR: The configuration file cannot be found at {configPath}\nUsing the one from '../config/config.yaml'.\nRemember you can specify alternative configuration file using --config argument.")
            return Path("../config/config.yaml")
        
        return configPath

