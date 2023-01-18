
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

gui = GuiThread(log, config, stats)
gui.daemon = True
gui.start()

for account in config.accounts:
    thread = FarmThread(log, config, account, stats)
    thread.daemon = True
    thread.start()
    farmThreads[account] = thread

for thread in farmThreads.values():
    try:
        while thread.is_alive():
            thread.join(1)
    except (KeyboardInterrupt, SystemExit):
        print('Exitting. Thank you for farming with us!')
        sys.exit()
