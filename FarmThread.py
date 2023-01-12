from threading import Thread
from time import sleep
from Browser import Browser


class FarmThread(Thread):
    """
    A thread that creates a capsule farm for a given account
    """

    def __init__(self, log, config, account):
        """
        Initializes the FarmThread

        :param log: Logger object
        :param config: Config object
        :param account: str, account name
        """
        super().__init__()
        self.log = log
        self.config = config
        self.account = account
        self.browser = Browser(self.log, self.config, self.account)

    def run(self):
        """
        Start watching every live match
        """
        self.log.info(f"Creating a farm for {self.account}")
        if self.browser.login(self.config.getAccount(self.account)["username"], self.config.getAccount(self.account)["password"]):
            self.log.info("Successfully logged in")
            while True:
                self.browser.getLiveMatches()
                self.browser.sendWatchToLive()
                self.log.debug(
                    f"{self.account} - Currently watching: {', '.join([m.league for m in self.browser.liveMatches.values()])}")
                sleep(Browser.STREAM_WATCH_INTERVAL)
        else:
            self.log.error("Login FAILED")

    def stop(self):
        """
        Try to stop gracefully
        """
        self.browser.stopMaintaininingSession()
