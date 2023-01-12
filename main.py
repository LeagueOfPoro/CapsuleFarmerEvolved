
from FarmThread import FarmThread
from Logger.Logger import Logger
from Config import Config
import sys
import argparse

CURRENT_VERSION = 0.1

parser = argparse.ArgumentParser(description='Farm Esports Capsules by watching all matches on lolesports.com.')
parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                    help='Path to a custom config file')
args = parser.parse_args()

print("*********************************************************")
print(f"*        Thank you for using Capsule Farmer v{CURRENT_VERSION}!       *")
print("* Please consider supporting League of Poro on YouTube. *")
print("*    If you need help with the app, join our Discord    *")
print("*             https://discord.gg/ebm5MJNvHU             *")
print("*********************************************************")
print()

config = Config(args.configPath)
log = Logger().createLogger(config.debug)

farmThreads = []

for account in config.accounts:
    thread = FarmThread(log, config, account)
    thread.daemon = True
    thread.start()
    farmThreads.append(thread)

for thread in farmThreads:
    try:
        while thread.is_alive():
            thread.join(1)
    except (KeyboardInterrupt, SystemExit):
        print('Exitting. Thank you for farming with us!')
        sys.exit()
