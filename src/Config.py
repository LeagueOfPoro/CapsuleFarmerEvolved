import re
from getpass import getpass
from pathlib import Path

import yaml
from rich import print
from yaml.parser import ParserError


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
        self.__loadConfig(configPath)
        try:
            bestStreams = Path("bestStreams.txt")
            if Path("../config/bestStreams.txt").exists():
                bestStreams = Path("../config/bestStreams.txt")
            elif Path("config/bestStreams.txt").exists():
                bestStreams = Path("config/bestStreams.txt")
            with open(bestStreams, "r", encoding="utf-8") as f:
                self.bestStreams = f.read().splitlines()
        except FileNotFoundError as ex:
            print(
                "[red]CRITICAL ERROR: The file bestStreams.txt was not found. Is it in the same folder as the executable?"
            )
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

    def __findConfig(self, configPath: str) -> Path:
        """
        Try to find configuartion file in alternative locations.

        :param configPath: user suplied configuartion file path
        :return: pathlib.Path, path to the configuration file
        """
        configFile = Path(configPath)
        if configFile.exists():
            return configFile

        _file = Path(__file__)
        src = _file.parent
        if src.name == "src":
            return src.parent / "config" / "config.yaml"
        else:
            return src / "config" / "config.yaml"

    def __loadConfig(self, configPath: str) -> None:
        """
        Try to load config file
        If file doens't exits create one then load it

        :param configFile: string, path to th config file
        """
        configFile = self.__findConfig(configPath)

        if not configFile.is_file():
            self.__createConfig(configFile)
        try:
            try:
                data = yaml.safe_load(configFile.read_text())
            except ParserError:
                print("[red]Config file is invalid")
                self.__createConfig(configFile)
                self.__loadConfig(configPath)
                return

            accounts = data["accounts"]
            for accountGroup in accounts:
                if self.__isValidAccount(accounts[accountGroup]):
                    self.accounts.update({accountGroup: accounts[accountGroup]})

            if len(self.accounts) == 0:
                print("[red]Found no valid accounts")
                self.__createConfig(configFile)
                self.__loadConfig(configPath)

            self.debug = data.get("debug", False)
            self.connectorDrops = data.get("connectorDropsUrl", "")
        except Exception as e:
            print("[red]Failed to load config file. Exiting")
            raise e

    def __createConfig(self, configFile: Path) -> None:
        """
        Create a config file and save it
        :param configFile: Path, path where the config file will be saved
        """
        print("[blue]Welcome to the config generator")
        print("[blue]For more information about what each setting does check the wiki")
        print("https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/wiki/Configuration")

        if not configFile.parent.is_dir():
            configFile.parent.mkdir()
        config = {}
        accs = {}
        while True:
            accs.update(
                {
                    getUserInput(
                        "Enter account group (unique name for each account group)"
                    ): {
                        "username": getUserInput("Enter account username"),
                        "password": getUserPassword(),
                    }
                }
            )
            if confirmPrompt("Add another account?"):
                continue
            else:
                break
        config.update({"accounts": accs})
        config.update(
            {
                "debug": confirmPrompt(
                    "Enable debug mode? (useful if encountering problems while program runs)"
                )
            }
        )
        if confirmPrompt("Enable connectorDropsUrl? (Discord webhook notifications)"):
            webhookRe = re.compile(r"https://discord.com/api/webhooks/(\d+)/(\w+)")
            url = getUserInput("Enter discord webhook url")
            if not webhookRe.match(url):
                print("[red]Invalid webhook url")
                print("Url shoudld look like https://discord.com/api/webhooks/id/token")
            else:
                config.update({"connectorDropsUrl": url})
        print("[green]Done!")
        print(f"[green]Writing to [/green][purple]{configFile}")
        exit()
        configFile.write_text(yaml.dump(config))

    def __isValidAccount(self, acc: dict[str, str]) -> bool:
        """
        Check if the account has default username and password
        """
        if (
            acc.get("username", "username") == "username"
            or acc.get("password", "password") == "password"
        ):
            return False
        return True


def getUserInput(prompt: str) -> str:
    """
    Get user input from terminal
    :param prompt: string, message to be displayed
    """
    print(prompt)
    return input("> ").strip()


def getUserPassword() -> str:
    print("Enter account password")
    return getpass("Password hidden > ")


def confirmPrompt(prompt: str) -> bool:
    """
    Allow user to confirm action
    :param prompt: string, message to be displayed
    """
    print(prompt)
    return input("[y/n]> ").lower().strip() in ["y", "yes"]
