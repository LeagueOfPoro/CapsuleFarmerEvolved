from Exceptions.CapsuleFarmerEvolvedException import CapsuleFarmerEvolvedException
from FarmThread import FarmThread
from GuiThread import GuiThread
from threading import Lock
from LoggerInit import LoggerInit
from Config import Config
import sys
import argparse
import logging
from rich import print
from pathlib import Path
from time import sleep

from Stats import Stats
from VersionManager import VersionManager

CURRENT_VERSION = 1.2


def init() -> tuple[logging.Logger, Config]:
    parser = argparse.ArgumentParser(description='Farm Esports Capsules by watching all matches on lolesports.com.')
    parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                        help='Path to a custom config file')
    args = parser.parse_args()

    print("*********************************************************")
    print(f"*   Thank you for using Capsule Farmer Evolved v{CURRENT_VERSION}!    *")
    print("* [steel_blue1]Please consider supporting League of Poro on YouTube.[/] *")
    print("*    If you need help with the app, join our Discord    *")
    print("*             https://discord.gg/ebm5MJNvHU             *")
    print("*********************************************************")
    print()

    Path("./logs/").mkdir(parents=True, exist_ok=True)
    Path("./sessions/").mkdir(parents=True, exist_ok=True)
    config = Config(args.configPath)
    log = LoggerInit.create_logger(False)
    if not VersionManager.is_latest_version(CURRENT_VERSION):
        log.warning(
            "!!! NEW VERSION AVAILABLE !!! Download it from: https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/releases/latest")
        print(
            "[bold red]!!! NEW VERSION AVAILABLE !!!\nDownload it from: https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/releases/latest\n")

    return log, config


def main(log: logging.Logger, config: Config):
    farm_threads = {}
    refresh_lock = Lock()
    locks = {"refreshLock": refresh_lock}
    stats = Stats(farm_threads)
    for account in config.accounts:
        stats.init_new_account(account)

    log.info(f"Starting a GUI thread.")
    gui = GuiThread(log, config, stats, locks)
    gui.daemon = True
    gui.start()

    while True:
        to_delete = []
        for account in config.accounts:
            if account not in farm_threads:
                if stats.get_failed_logins(account) < 3:
                    if stats.get_failed_logins(account) > 0:
                        log.debug("Sleeping {account} before retrying login.")
                        sleep(30)
                    log.info(f"Starting a thread for {account}.")
                    thread = FarmThread(log, config, account, stats, locks)
                    thread.daemon = True
                    thread.start()
                    farm_threads[account] = thread
                    log.info(f"Thread for {account} was created.")
                else:
                    stats.update_status(account, "[red]LOGIN FAILED")
                    log.error(f"Maximum login retries reached for account {account}")
                    to_delete.append(account)
        if not farm_threads:
            break
        for account in to_delete:
            del config.accounts[account]

        to_delete = []
        for account in farm_threads:
            if farm_threads[account].is_alive():
                farm_threads[account].join(1)
            else:
                to_delete.append(account)
                log.warning(f"Thread {account} has finished.")
        for account in to_delete:
            del farm_threads[account]


if __name__ == '__main__':
    try:
        log_instance, loaded_config = init()
        main(log_instance, loaded_config)
    except (KeyboardInterrupt, SystemExit):
        print('Exiting. Thank you for farming with us!')
        sys.exit()
    except CapsuleFarmerEvolvedException as e:
        # Added null check to prevent issues with failure in init.
        if log_instance is None:
            LoggerInit.create_logger(False).error(f'An error has occurred: {e}')
        else:
            log_instance.error(f'An error has occurred: {e}')
