import re
from getpass import getpass
from os.path import isfile
from typing import Any
import yaml
from rich import print


def createConfig(configPath: str) -> None:  # noqa
    print("[green]Welcome to the configuration file generator!")
    if not confirmPrompt("Do you want to continue?"):
        print("Exiting...")
        exit(0)

    webhook_re = re.compile(r"https://discord.com/api/webhooks/(\d+)/(\w+)")

    config: dict[str, Any] = {}
    accs: dict[str, dict[str, str]] = {}

    while True:
        accGroup = getInput("Enter group name (No spaces, no special characters, should be recognizable)")
        accName = getInput("Enter [red]Riot username[/red] (used to log in to the game)")
        print("Enter [red]Riot password[/red] (used to log in to the game)")
        accPassword = getpass("(PASSWORD HIDDEN): ")
        accs[accGroup] = {"username": accName, "password": accPassword}

        if not confirmPrompt("Do you want to add another account?"):
            break

    config["accounts"] = accs
    config["debug"] = confirmPrompt("Do you want to enable debug mode?")
    if not confirmPrompt("[bold]Continue with advanced settings?"):
        print(f"Done! Writing configuration file {configPath}")
        with open(configPath, "w", encoding="utf-8") as f:
            yaml.dump(config, f)
        return

    print("[bold][red]Advanced settings")
    print("[green]Read more about them here:")
    print(
        "https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/blob/master/README.md#Configuration"
    )

    if confirmPrompt("Enable connectorDropsUrl?"):
        while True:
            connectorDropsUrl = getInput("Enter the webhook URL")
            if not webhook_re.match(connectorDropsUrl):
                print(
                    "Webhook URL seems invalid. Should start with https://discord.com/api/webhooks/"
                )
                if not confirmPrompt("Do you want to try again"):
                    break
            else:
                config["connectorDropsUrl"] = connectorDropsUrl
                break

    print(f"[green]Done![/green] This will write configuration file {configPath}")

    with open(configPath, "w", encoding="utf-8") as f:
        yaml.dump(config, f)

invalidUsernames = ["", "username"]
invalidPasswords = ["", "password"]

def validateConfig(configPath: str) -> bool:
    if not isfile(configPath):
        return False

    with open(configPath, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

        try:
            accounts = config["accounts"]
            for acc in accounts.values():
                if (
                    acc["username"] in invalidUsernames
                    or acc["password"] in invalidPasswords
                ):
                    return False

        except KeyError:
            return False

    return True

def getInput(prompt: str) -> str:
    print(prompt)
    return input("> ").strip()

def confirmPrompt(prompt: str) -> bool:
    print(prompt)
    inp = input("[y/n]> ").strip().lower()

    if inp in ["y", "yes"]:
        return True
    else:
        return False
