import yaml
from yaml.parser import ParserError
from rich import print

from Exceptions.InvalidCredentialsException import InvalidCredentialsException


class Config:
    """
    A class that loads and stores the configuration
    """

    def __init__(self, config_path: str) -> None:
        """
        Loads the configuration file into the Config object

        :param config_path: string, path to the configuration file
        """
        
        self.accounts = {}
        try:
            with open(config_path, "r", encoding='utf-8') as f:
                config = yaml.safe_load(f)
                all_accounts = config.get("accounts")
                only_default_username = True
                for account in all_accounts:
                    self.accounts[account] = {
                        "username": all_accounts[account]["username"],
                        "password": all_accounts[account]["password"],
                    }
                    if "username" != all_accounts[account]["username"]:
                        only_default_username = False
                if only_default_username:
                    raise InvalidCredentialsException                    
                self.debug = config.get("debug", False)
                self.connectorDrops = config.get("connectorDropsUrl", "")
        except FileNotFoundError as ex:
            print(f"[red]CRITICAL ERROR: The configuration file cannot be found at {config_path}\nHave you extracted the ZIP archive and edited the configuration file?")
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

    def get_account(self, account: str) -> dict:
        """
        Get account information

        :param account: string, name of the account
        :return: dictionary, account information
        """
        return self.accounts[account]
