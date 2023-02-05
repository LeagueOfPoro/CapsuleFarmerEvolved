from datetime import datetime
from threading import Thread
from time import sleep
from Browser import Browser
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
        self.browser = Browser(self.log, self.config, self.account)
        self.locks = locks

    def run(self):
        """
        Start watching every live match
        """
        try:
            self.stats.update_status(self.account, "[green]LOGIN")
            if self.browser.login(self.config.get_account(self.account)["username"],
                                  self.config.get_account(self.account)["password"],
                                  self.locks["refreshLock"]):
                self.stats.update_status(self.account, "[green]LIVE")
                self.stats.reset_login_failed(self.account)
                while True:
                    self.browser.maintain_session()
                    self.browser.get_live_matches()
                    self.browser.send_watch_to_live()
                    new_drops = []
                    if self.browser.liveMatches:
                        live_matches_status = []
                        for m in self.browser.liveMatches.values():
                            live_matches_status.append(f"{m.league}")
                        self.log.debug(f"{', '.join(live_matches_status)}")
                        live_matches_msg = f"{', '.join(live_matches_status)}"
                        new_drops = self.browser.check_new_drops(self.stats.get_last_drop_check(self.account))
                        self.stats.update_last_drop_check(self.account, int(datetime.now().timestamp() * 1e3))
                    else:
                        live_matches_msg = "None"
                    self.stats.update(self.account, len(new_drops), live_matches_msg)
                    if self.config.connectorDrops:
                        self.__notify_connector_drops(new_drops)
                    sleep(Browser.STREAM_WATCH_INTERVAL)
            else:
                self.log.error(f"Login for {self.account} FAILED!")
                self.stats.add_login_failed(self.account)
                if self.stats.get_failed_logins(self.account) < 3:
                    self.stats.update_status(self.account, "[red]LOGIN FAILED - WILL RETRY SOON")
                else:
                    self.stats.update_status(self.account, "[red]LOGIN FAILED")
        except Exception:
            # TODO: Implement proper error handling.
            self.log.exception(f"Error in {self.account}. The program will try to recover.")

    def stop(self):
        """
        Try to stop gracefully
        """
        self.browser.stopMaintaininingSession()

    def __notify_connector_drops(self, new_drops: list):
        if new_drops:
            if "https://discord.com/api/webhooks" in self.config.connectorDrops:
                for x in range(len(new_drops)):
                    title = new_drops[x]["dropsetTitle"]
                    thumbnail = new_drops[x]["dropsetImages"]["cardUrl"]
                    reward = new_drops[x]["inventory"][0]["localizedInventory"]["title"]["en_US"]
                    rewardImage = new_drops[x]["inventory"][0]["localizedInventory"]["inventory"]["imageUrl"]

                    embed = {
                        "title": f"[{self.account}] {title}",
                        "description": f"We claimed an **{reward}** from <https://lolesports.com/rewards>",
                        "image": {"url": f"{thumbnail}"},
                        "thumbnail": {"url": f"{rewardImage}"},
                        "color": 6676471,
                    }

                    params = {
                        "username": "CapsuleFarmerEvolved",
                        "embeds": [embed]
                    }
                    requests.post(self.config.connectorDrops, headers={"Content-type": "application/json"}, json=params)
            else:
                requests.post(self.config.connectorDrops, json=new_drops)
