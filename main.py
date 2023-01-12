
from FarmThread import FarmThread
from Logger.Logger import Logger
from Config import Config
from Browser import Browser
import sys


config = Config()
log = Logger().createLogger(config.debug)

farmThreads = []

for account in config.accounts:
    thread = FarmThread(log, config, account)
    thread.start()
    farmThreads.append(thread)

for thread in farmThreads:
    try:
        while thread.is_alive():
            thread.join(1)
    except (KeyboardInterrupt, SystemExit):
        print('Exitting. Thank you for farming with us!')
        for thread in farmThreads:
            if thread.is_alive():
                thread.stop()
        sys.exit()
