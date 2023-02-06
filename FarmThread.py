from datetime import datetime
from threading import Thread
from time import sleep
from Browser import Browser
import requests
supported = False

try:
    import simpleaudio as sa
    from win10toast import ToastNotifier
    supported = True
except ImportError:
    pass
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
        self.browser = Browser(self.log, stats, self.config, self.account)
        self.locks = locks

    def run(self):
        """
        Start watching every live match
        """
        try:
            self.stats.updateStatus(self.account, "[yellow]LOGIN")
            if self.browser.login(self.config.getAccount(self.account)["username"], self.config.getAccount(self.account)["password"], self.locks["refreshLock"]):
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
                    if self.config.notifyToast:
                        if supported == True:
                            self.__notifactionToast(newDrops)
                    if newDrops:
                        if self.config.notifyDropSound:
                            if supported == True:
                                wave_obj = sa.WaveObject.from_wave_file(self.config.notifyDropSound)
                                play_obj = wave_obj.play()
                                play_obj.wait_done()

                    sleep(Browser.STREAM_WATCH_INTERVAL)
            else:
                self.log.error(f"Login for {self.account} FAILED!")
                self.stats.addLoginFailed(self.account)
                if self.stats.getFailedLogins(self.account) < 3:
                    self.stats.updateStatus(self.account, "[red]LOGIN FAILED - WILL RETRY SOON")
                else:
                    self.stats.updateStatus(self.account, "[red]LOGIN FAILED")
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

    def __notifactionToast(self, newDrops: list):
        if newDrops:
            for x in range(len(newDrops)):
                title = newDrops[x]["dropsetTitle"]
                reward = newDrops[x]["inventory"][0]["localizedInventory"]["title"]["en_US"]
                toast = ToastNotifier()
                toast.show_toast(
                    f"The account [{self.account}] received a reward! ({title})",
                    f"We claimed an {reward} from https://lolesports.com/rewards",
                    icon_path="poro.ico",
                    duration=5,
                    threaded=True,

                )
                while toast.notification_active(): sleep(1)