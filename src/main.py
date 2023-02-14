import argparse
from pathlib import Path
import sys

from rich import print

from Config import Config
from Logger import Logger
from MasterThread import MasterThread
from Stats import Stats
from VersionManager import VersionManager


CURRENT_VERSION = 1.3

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Farm Esports Capsules by watching all matches on lolesports.com.')
    parser.add_argument('-c', '--config', dest="configPath", default="./config.secret.yaml",
                        help='Path to a custom config file')

    # We need to get rid of the --config argument, otherwise Kivy will complain
    args, unknown = parser.parse_known_args()
    sys.argv[1:] = unknown

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
    log = Logger.createLogger(True)
    if not VersionManager.isLatestVersion(CURRENT_VERSION):
        log.warning(
            "!!! NEW VERSION AVAILABLE !!! Download it from: https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/releases/latest")
        print("[bold red]!!! NEW VERSION AVAILABLE !!!\nDownload it from: https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/releases/latest\n")

    stats = Stats()
    masterThread = MasterThread(log, config, stats)
    masterThread.daemon = True
    masterThread.start()

    if config.disableGui:
        masterThread.join()
    else:
        # Import GUI only if needed
        from GuiThread import GuiThread
        GuiThread(stats).run()
