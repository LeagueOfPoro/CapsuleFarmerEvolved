from threading import Thread
from time import sleep
from Browser import Browser

class FarmThread(Thread):
    def __init__(self, log, config, account):
        super().__init__()
        self.log = log
        self.config = config
        self.account = account
        self.browser = Browser(self.log, self.config, self.account)

    def run(self):
        self.log.info(f"Creating a farm for {self.account}")
        if self.browser.login(self.config.getAccount(self.account)["username"], self.config.getAccount(self.account)["password"]):
            self.log.info("Successfully logged in")
            while True:
                self.browser.getLiveMatches()
                self.browser.cleanUpWatchlist()
                self.browser.sendWatchToLive()
                # self.browser.startWatchingNewMatches()
                self.log.debug(f"Currently watching: {', '.join([m.league for m in self.browser.liveMatches.values()])}")
                sleep(Browser.STREAM_WATCH_INTERVAL)
        else:
            self.log.error("Login FAILED")

    
    def stop(self):
        self.browser.stopMaintaininingSession()
        self.browser.stopWatchingAll()