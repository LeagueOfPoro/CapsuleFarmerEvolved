from threading import Thread
from time import sleep
from Browser import Browser


class FarmThread(Thread):
    """
    A thread that creates a capsule farm for a given account
    """

    def __init__(self, log, config, account, stats):
        """
        Initializes the FarmThread

        :param log: Logger object
        :param config: Config object
        :param account: str, account name
        :param stats: Stats, Stats object
        """
        super().__init__()
        self.log = log
        self.config = config
        self.account = account
        self.stats = stats
        self.browser = Browser(self.log, self.config, self.account)

    def run(self):
        """
        Start watching every live match
        """
        try:
            self.stats.updateStatus(self.account, "[green]LOGIN")
            if self.browser.login(self.config.getAccount(self.account)["username"], self.config.getAccount(self.account)["password"]):
                self.stats.updateStatus(self.account, "[green]LIVE")
                self.stats.resetLoginFailed(self.account)
                while True:
                    self.browser.getLiveMatches()
                    dropsAvailable = self.browser.sendWatchToLive()
                    if self.browser.liveMatches:
                        liveMatchesStatus = []
                        for m in self.browser.liveMatches.values():
                            status = dropsAvailable.get(m.league, False)
                            liveMatchesStatus.append(f"{'[green1]' if status else '[orange1]'}{m.league}{'[/]'}")
                        self.log.debug(f"{', '.join(liveMatchesStatus)}")    
                        liveMatchesMsg = f"{', '.join(liveMatchesStatus)}"
                    else:
                        liveMatchesMsg = "None"
                    self.stats.update(self.account, 0, liveMatchesMsg)
                    sleep(Browser.STREAM_WATCH_INTERVAL)
            else:
                self.log.error(f"Login for {self.account} FAILED!")
                self.stats.updateStatus(self.account, "[red]LOGIN FAILED")
                self.stats.addLoginFailed(self.account)
        except Exception:
            self.log.exception(f"Error in {self.account}. The program will try to recover.")


    def stop(self):
        """
        Try to stop gracefully
        """
        self.browser.stopMaintaininingSession()
