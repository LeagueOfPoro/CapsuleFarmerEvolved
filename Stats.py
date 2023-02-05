from datetime import datetime


class Stats:
    def __init__(self, farm_threads) -> None:
        self.farmThreads = farm_threads
        self.accountData = {}

    def init_new_account(self, account_name: str):
        self.accountData[account_name] = {"lastCheck": "", "totalDrops": 0, "lastDrop": "N/A", "liveMatches": "",
                                          "status": "[yellow]WAIT", "failedLoginCounter": 0,
                                          "lastDropCheck": int(datetime.now().timestamp() * 1e3)}

    def update(self, account_name: str, new_drops: int = 0, live_matches: str = ""):
        self.accountData[account_name]["lastCheck"] = datetime.now().strftime("%H:%M:%S %d/%m")
        self.accountData[account_name]["liveMatches"] = live_matches
        if new_drops > 0:
            self.accountData[account_name]["totalDrops"] += new_drops
            self.accountData[account_name]["lastDrop"] = datetime.now().strftime("%H:%M:%S %d/%m")

    def update_status(self, account_name: str, msg: str):
        self.accountData[account_name]["status"] = msg

    def update_last_drop_check(self, account_name: str, last_drop_check: int):
        self.accountData[account_name]["lastDropCheck"] = last_drop_check

    def get_last_drop_check(self, account_name: str) -> int:
        return self.accountData[account_name]["lastDropCheck"]

    def add_login_failed(self, account_name: str):
        self.accountData[account_name]["failedLoginCounter"] += 1

    def reset_login_failed(self, account_name: str):
        self.accountData[account_name]["failedLoginCounter"] = 0

    def get_failed_logins(self, account_name: str):
        return self.accountData[account_name]["failedLoginCounter"]
