from DataProviderThread import DataProviderThread
from Exceptions.CapsuleFarmerEvolvedException import CapsuleFarmerEvolvedException
from FarmThread import FarmThread
from GuiThread import GuiThread
from threading import Lock
from Config import Config
from Logger import Logger
import logging
import sys
import argparse
from rich import print
from pathlib import Path
from time import sleep, strftime, localtime
from Restarter import Restarter
from SharedData import SharedData

from Stats import Stats
from VersionManager import VersionManager

<<<<<<< HEAD
CURRENT_VERSION = 1.3
=======
CURRENT_VERSION = 1.4
>>>>>>> 0f35a8111b440fc0676ccb62e7934dadf4eedf1c

def init() -> tuple[logging.Logger, Config]:
    parser = argparse.ArgumentParser(description='Farm Esports Capsules by watching all matches on lolesports.com.')
    parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                        help='Path to a custom config file')
    args = parser.parse_args()

    print("*********************************************************")
    print(f"*   Thank you for using Capsule Farmer Evolved v{str(CURRENT_VERSION)}!    *")
    print("* [steel_blue1]Please consider supporting League of Poro on YouTube.[/] *")
    print("*    If you need help with the app, join our Discord    *")
    print("*             https://discord.gg/ebm5MJNvHU             *")
    print(f"*                 Started: [green]{strftime('%b %d, %H:%M', localtime())}[/]                *")
    print("*********************************************************")
    print()

    Path("./logs/").mkdir(parents=True, exist_ok=True)
    Path("./sessions/").mkdir(parents=True, exist_ok=True)
    config = Config(args.configPath)
    log = Logger.createLogger(config.debug, CURRENT_VERSION)
    if not VersionManager.isLatestVersion(CURRENT_VERSION):
        log.warning("!!! NEW VERSION AVAILABLE !!! Download it from: https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/releases/latest")
        print("[bold red]!!! NEW VERSION AVAILABLE !!!\nDownload it from: https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/releases/latest\n")

    return log, config

def main(log: logging.Logger, config: Config):
    farmThreads = {}
    refreshLock = Lock()
    locks = {"refreshLock": refreshLock}

    sharedData = SharedData()
    stats = Stats()

    for account in config.accounts:
        stats.initNewAccount(account)

    restarter = Restarter(stats)

    log.info(f"Starting a GUI thread.")
    guiThread = GuiThread(log, config, stats, locks)
    guiThread.daemon = True
    guiThread.start()

    dataProviderThread = DataProviderThread(log, config, sharedData)
    dataProviderThread.daemon = True
    dataProviderThread.start()

    while True:
        for account in config.accounts:
            if account not in farmThreads and restarter.canRestart(account) and stats.getThreadStatus(account):
                log.info(f"Starting a thread for {account}.")
                thread = FarmThread(log, config, account, stats, locks, sharedData)
                thread.daemon = True
                thread.start()
                farmThreads[account] = thread
                log.info(f"Thread for {account} was created.")

            if account in farmThreads and not stats.getThreadStatus(account):
                del farmThreads[account]

        toDelete = []
        
        for account in farmThreads:
            if not farmThreads[account].is_alive():
                toDelete.append(account)
                log.warning(f"Thread {account} has finished.")
                restarter.setRestartDelay(account)
                stats.updateStatus(account, f"[red]ERROR - restart at {restarter.getNextStart(account).strftime('%H:%M:%S')}, failed logins: {stats.getFailedLogins(account)}")
                log.warning(f"Thread {account} has finished and will restart at {restarter.getNextStart(account).strftime('%H:%M:%S')}. Number of consecutively failed logins: {stats.getFailedLogins(account)}")
                
        for account in toDelete:
            del farmThreads[account]

<<<<<<< HEAD
=======
        sleep(5)
>>>>>>> 0f35a8111b440fc0676ccb62e7934dadf4eedf1c
if __name__ == '__main__':
    log = None
    try:
        log, config = init()
        main(log, config)
    except (KeyboardInterrupt, SystemExit):
        print('Exiting. Thank you for farming with us!')
        sys.exit()
    except CapsuleFarmerEvolvedException as e:
        if isinstance(log, logging.Logger):
            log.error(f"An error has occurred: {e}")
        else:
            print(f'[red]An error has occurred: {e}')
