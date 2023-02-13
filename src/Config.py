import requests
import yaml
from yaml.parser import ParserError
from rich import print
from pathlib import Path
import getpass

from Exceptions.InvalidCredentialsException import InvalidCredentialsException


class Config:
    """
    A class that loads and stores the configuration
    """

    REMOTE_BEST_STREAMS_URL = "https://raw.githubusercontent.com/LeagueOfPoro/CapsuleFarmerEvolved/master/config/bestStreams.txt"

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
                            "username": accs[account]["username"],
                            "password": accs[account]["password"]
                        }                    
                if not self.accounts:
                    raise InvalidCredentialsException                    
                self.debug = config.get("debug", False)
                self.connectorDrops = config.get("connectorDropsUrl", "")
        except FileNotFoundError as ex:
            print(f"[red]CRITICAL ERROR: The configuration file cannot be found at {configPath}\nHave you extracted the ZIP archive and edited the configuration file?")
            if UserPrompt("Do you want to create config file and add new account? (Y/N): "):
                
                 
                self.addAccount(configPath,1) 
                self.__init__(configPath)  
                  
                
            else: raise ex
            
        except (ParserError, KeyError) as ex:
            print(f"[red]CRITICAL ERROR: The configuration file does not have a valid format.\nPlease, check it for extra spaces and other characters.\nAlternatively, use confighelper.html to generate a new one.")
            print("Press any key to exit...")
            input()
            raise ex
        except InvalidCredentialsException as ex:
            print(f"[red]CRITICAL ERROR: There are only default credentials in the configuration file.\nYou need to add you Riot account login to config.yaml to receive drops.")
            
            if UserPrompt("Do you want to add new account? (Y/N): "):
                
                self.debug = config.get("debug", False)
                self.connectorDrops = config.get("connectorDropsUrl", "")   
                self.addAccount(configPath,1)    
                
            else: raise ex

        # Get bestStreams from URL
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

        :param configPath: user suplied configuration file path
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
    def addAccount(self,configPath,new):
        """
        Add account to config.yaml file

        :param configPath: user suplied configuration file path
        :param new: pass 'False' if you want to append to config file or 'True' if you want to rewrite it completely

        """
        
        name= input("Enter desired name for your account: ")
        
        username= input("Enter your username: ")
        
        password= getpass.getpass("Enter your password: ")
        self.accounts[name] = {
                    "username": username,
                    "password": password
                                }
        configPath = self.__findConfig(configPath)
        
        f = open(configPath, "w" if new else "a", encoding='utf-8')
         
        f.write(yaml.dump({'accounts':self.accounts})) 
        if UserPrompt("Do you want to add another account? (Y/N): ") :
            self.addAccount(configPath,0)
              
        
def UserPrompt(text):
    """
    Prompt user with the passed text

    :param text: Text you want to display
    :return: True or False depending on user's input
    """
    a= input(text).lower()
    if a=='y' or a=='yes':
        return True
    else: return False                       
