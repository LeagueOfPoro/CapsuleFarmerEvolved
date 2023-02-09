from datetime import datetime
from threading import Thread
from time import sleep
from Browser import Browser
from Exceptions.InvalidIMAPCredentials import InvalidIMAPCredentialsException
import requests

class FarmThread(Thread):
    """
    A thread that creates a capsule farm for a given account
    """

    def __init__(self, log, config, account, stats, locks):
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
        self.browser = Browser(self.log, self.stats, self.config, self.account)
        self.locks = locks

    def run(self):
        """
        Start watching every live match
        """
        try:
            self.stats.updateStatus(self.account, "[green]LOGIN")
            if self.browser.login(self.config.getAccount(self.account)["username"], self.config.getAccount(self.account)["password"], self.config.getAccount(self.account)["imapusername"], self.config.getAccount(self.account)["imappassword"], self.config.getAccount(self.account)["imapserver"], self.locks["refreshLock"]):
                self.stats.updateStatus(self.account, "[green]LIVE")
                self.stats.resetLoginFailed(self.account)
                while True:
                    self.browser.maintainSession()
                    self.browser.getLiveMatches()
                    self.browser.sendWatchToLive()
                    newDrops = []
                    if self.browser.liveMatches:
                        liveMatchesStatus = []
                        for m in self.browser.liveMatches.values():
                            liveMatchesStatus.append(f"{m.league}")
                        self.log.debug(f"{', '.join(liveMatchesStatus)}")    
                        liveMatchesMsg = f"{', '.join(liveMatchesStatus)}"
                        newDrops = self.browser.checkNewDrops(self.stats.getLastDropCheck(self.account))
                        self.stats.updateLastDropCheck(self.account, int(datetime.now().timestamp()*1e3))
                    else:
                        liveMatchesMsg = "None"
                    self.stats.update(self.account, len(newDrops), liveMatchesMsg)
                    if self.config.connectorDrops:
                        self.__notifyConnectorDrops(newDrops)
                    sleep(Browser.STREAM_WATCH_INTERVAL)
            else:
                self.log.error(f"Login for {self.account} FAILED!")
                self.stats.addLoginFailed(self.account)
                if self.stats.getFailedLogins(self.account) < 3:
                    self.stats.updateStatus(self.account, "[red]LOGIN FAILED - WILL RETRY SOON")
                else:
                    self.stats.updateStatus(self.account, "[red]LOGIN FAILED")
        except (Exception, InvalidIMAPCredentialsException):
            if InvalidIMAPCredentialsException:
                self.log.error(f"IMAP login failed for {self.account}")
                self.stats.updateStatus(self.account, "[red]IMAP LOGIN FAILED")
                self.stats.updateThreadStatus(self.account)
            else:
                self.log.exception(f"Error in {self.account}. The program will try to recover.")

    def stop(self):
        """
        Try to stop gracefully
        """
        self.browser.stopMaintaininingSession()

    def __notifyConnectorDrops(self, newDrops: list):
        if newDrops:
            if "https://discord.com/api/webhooks" in self.config.connectorDrops:
                for x in range(len(newDrops)):
                    title = newDrops[x]["dropsetTitle"]
                    thumbnail = newDrops[x]["dropsetImages"]["cardUrl"]
                    reward = newDrops[x]["inventory"][0]["localizedInventory"]["title"]["en_US"]
                    rewardImage = newDrops[x]["inventory"][0]["localizedInventory"]["inventory"]["imageUrl"]

                    embed = {
                        "title": f"[{self.account}] {title}",
                        "description": f"We claimed an **{reward}** from <https://lolesports.com/rewards>",
                        "image" : {"url": f"{thumbnail}"},
                        "thumbnail": {"url": f"{rewardImage}"},
                        "color": 6676471,
                    }

                    params = {
                        "username" : "CapsuleFarmerEvolved",
                        "embeds": [embed]
                    }
                    requests.post(self.config.connectorDrops, headers={"Content-type":"application/json"}, json=params)
            else:
                requests.post(self.config.connectorDrops, json=newDrops)
