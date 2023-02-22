from datetime import datetime
from threading import Thread
from time import sleep
from Browser import Browser
from Config import Config
from Exceptions.InvalidIMAPCredentialsException import InvalidIMAPCredentialsException
from Exceptions.Fail2FAException import Fail2FAException
import requests

from SharedData import SharedData

class FarmThread(Thread):
    """
    A thread that creates a capsule farm for a given account
    """

    def __init__(self, log, config, account, stats, locks, sharedData: SharedData):
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
        self.browser = Browser(self.log, self.stats, self.config, self.account, sharedData)
        self.locks = locks
        self.sharedData = sharedData

    def run(self):
        """
        Start watching every live match
        """
        try:
            self.stats.updateStatus(self.account, "[yellow]LOGIN")

            if self.browser.login(self.config.getAccount(self.account)["username"], self.config.getAccount(self.account)["password"], self.config.getAccount(self.account)["imapUsername"], self.config.getAccount(self.account)["imapPassword"], self.config.getAccount(self.account)["imapServer"], self.locks["refreshLock"]):
                self.stats.resetLoginFailed(self.account)
                self.stats.updateStatus(self.account, "[green]LIVE")
                _, totalDrops = self.browser.checkNewDrops(0)
                self.stats.setTotalDrops(self.account, totalDrops)
                while True:
                    self.browser.maintainSession()
                    watchFailed = self.browser.sendWatchToLive()
                    newDrops = []
                    if self.sharedData.getLiveMatches():
                        liveMatchesStatus = []
                        for m in self.sharedData.getLiveMatches().values():
                            if m.league in watchFailed:
                                self.stats.updateStatus(self.account, "[red]RIOT SERVERS OVERLOADED - PLEASE WAIT")
                            else:
                                self.stats.updateStatus(self.account, "[green]LIVE")
                            liveMatchesStatus.append(m.league)
                        self.log.debug(f"Live matches: {', '.join(liveMatchesStatus)}")
                        liveMatchesMsg = f"{', '.join(liveMatchesStatus)}"
                        newDrops, totalDrops = self.browser.checkNewDrops(self.stats.getLastDropCheck(self.account))
                        self.stats.setTotalDrops(self.account, totalDrops)
                        self.stats.updateLastDropCheck(self.account, int(datetime.now().timestamp() * 1e3))
                    else:
                        liveMatchesMsg = self.sharedData.getTimeUntilNextMatch()
                    try:
                        if newDrops and getLeagueFromID(newDrops[-1]["leagueID"]):
                            self.stats.update(self.account, len(newDrops), liveMatchesMsg, getLeagueFromID(newDrops[-1]["leagueID"]))
                        else:
                            self.stats.update(self.account, 0, liveMatchesMsg)
                    except (IndexError, KeyError):
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
        except InvalidIMAPCredentialsException:
            self.log.error(f"IMAP login failed for {self.account}")
            self.stats.updateStatus(self.account, "[red]IMAP LOGIN FAILED")
            self.stats.updateThreadStatus(self.account)
        except Exception:
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

def getLeagueFromID(leagueId):
    allLeagues = getLeagues()
    for league in allLeagues:
        if leagueId in league["id"]:
            return league["name"]
    return ""
def getLeagues():
    headers = {"Origin": "https://lolesports.com", "Referrer": "https://lolesports.com",
               "x-api-key": Config.RIOT_API_KEY}
    res = requests.get(
        "https://esports-api.lolesports.com/persisted/gw/getLeagues?hl=en-GB", headers=headers)
    leagues = res.json()["data"].get("leagues", [])
    res.close()
    return leagues