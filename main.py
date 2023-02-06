import argparse
import sys
from pathlib import Path
from threading import Lock
from time import sleep
from rich import print

from Config import Config
from CreateConfigFile import createConfig, validateConfig
from Exceptions.CapsuleFarmerEvolvedException import CapsuleFarmerEvolvedException
from FarmThread import FarmThread
from GuiThread import GuiThread
from Logger import Logger
from Stats import Stats
from VersionManager import VersionManager

CURRENT_VERSION = 1.2

def init() -> tuple[Logger, Config]:
    parser = argparse.ArgumentParser(
        description="Farm Esports Capsules by watching all matches on lolesports.com."
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="configPath",
        default="./config.yaml",
        help="Path to a custom config file",
    )

    parser.add_argument(
        "--create-config", action="store_true", help="Create a config file"
    )
    args = parser.parse_args()

    print("*********************************************************")
    print(f"*   Thank you for using Capsule Farmer Evolved v{CURRENT_VERSION}!    *")
    print("* [steel_blue1]Please consider supporting League of Poro on YouTube.[/] *")
    print("*    If you need help with the app, join our Discord    *")
    print("*             https://discord.gg/ebm5MJNvHU             *")
    print("*********************************************************")
    print()

    if args.create_config or not validateConfig(args.configPath):
        createConfig(args.configPath)

    Path("./logs/").mkdir(parents=True, exist_ok=True)
    Path("./sessions/").mkdir(parents=True, exist_ok=True)
    config = Config(args.configPath)
    log = Logger().createLogger(config.debug)
    if not VersionManager.isLatestVersion(CURRENT_VERSION):
        log.warning(
            "!!! NEW VERSION AVAILABLE !!! Download it from: https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/releases/latest"
        )
        print(
            "[bold red]!!! NEW VERSION AVAILABLE !!!\nDownload it from: https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/releases/latest\n"
        )

    return log, config


def main(log: Logger, config: Config):
    farmThreads = {}
    refreshLock = Lock()
    locks = {"refreshLock": refreshLock}
    stats = Stats(farmThreads)

    for account in config.accounts:
        stats.initNewAccount(account)

    log.info(f"Starting a GUI thread.")
    gui = GuiThread(log, config, stats, locks)
    gui.daemon = True
    gui.start()

    while True:
        toDelete = []
        for account in config.accounts:
            if account not in farmThreads:
                if stats.getFailedLogins(account) < 3:
                    if stats.getFailedLogins(account) > 0:
                        log.debug("Sleeping {account} before retrying login.")
                        sleep(30)
                    log.info(f"Starting a thread for {account}.")
                    thread = FarmThread(log, config, account, stats, locks)
                    thread.daemon = True
                    thread.start()
                    farmThreads[account] = thread
                    log.info(f"Thread for {account} was created.")
                else:
                    stats.updateStatus(account, "[red]LOGIN FAILED")
                    log.error(f"Maximum login retries reached for account {account}")
                    toDelete.append(account)
        if not farmThreads:
            break
        for account in toDelete:
            del config.accounts[account]

        toDelete = []
        for account in farmThreads:
            if farmThreads[account].is_alive():
                farmThreads[account].join(1)
            else:
                toDelete.append(account)
                log.warning(f"Thread {account} has finished.")
        for account in toDelete:
            del farmThreads[account]


if __name__ == "__main__":
    try:
        log, config = init()
        main(log, config)
    except (KeyboardInterrupt, SystemExit):
        print("Exitting. Thank you for farming with us!")
        sys.exit()
    except CapsuleFarmerEvolvedException as e:
        log.error(f"An error has occured: {e}")
