
from FarmThread import FarmThread
from GuiThread import GuiThread
from Logger.Logger import Logger
from Config import Config
import sys
import argparse
from rich import print

from Stats import Stats
from VersionManager import VersionManager

CURRENT_VERSION = 0.3

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


config = Config(args.configPath)
log = Logger().createLogger(config.debug)
if not VersionManager.isLatestVersion(CURRENT_VERSION):
    log.warning("!!! NEW VERSION AVAILABLE !!! Download it from: https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/releases/latest")
    print("[bold red]!!! NEW VERSION AVAILABLE !!!\nDownload it from: https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/releases/latest\n")

farmThreads = {}
stats = Stats(farmThreads)
for account in config.accounts:
    stats.initNewAccount(account)

log.info(f"Starting a GUI thread.")
gui = GuiThread(log, config, stats)
gui.daemon = True
gui.start()

try:
    while True:
        for account in config.accounts:
            if account not in farmThreads:
                log.info(f"Starting a thread for {account}.")
                thread = FarmThread(log, config, account, stats)
                thread.daemon = True
                thread.start()
                farmThreads[account] = thread
                log.info(f"Thread for {account} was created.")
        if not farmThreads:
            break

        toDelete = []
        for account in farmThreads:
            if farmThreads[account].is_alive():
                farmThreads[account].join(1)
            else:
                toDelete.append(account)
                log.warning(f"Thread {account} has finished.")
        for account in toDelete:
            del farmThreads[account]
except (KeyboardInterrupt, SystemExit):
        print('Exitting. Thank you for farming with us!')
        sys.exit()
