from datetime import datetime
import json

class Stats:
    def __init__(self, farmThreads) -> None:
        self.farmThreads = farmThreads
        self.accountData = {}

    def initNewAccount(self, accountName: str):
        totalDrops = self.loadTotalDrops(accountName)
        self.accountData[accountName] = {
            "lastCheck": "",
            "totalDrops": totalDrops,
            "sessionDrops": 0,
            "lastDrop": "N/A",
            "liveMatches": "",
            "status": "[yellow]WAIT",
            "failedLoginCounter": 0,
            "lastDropCheck": int(datetime.now().timestamp()*1e3)
        }

    def update(self, accountName: str, newDrops: int = 0, liveMatches: str = "", lastDropleague: str = None):
        self.accountData[accountName]["lastCheck"] = datetime.now().strftime("%H:%M:%S %d/%m")
        self.accountData[accountName]["liveMatches"] = liveMatches
        if newDrops > 0:
            self.accountData[accountName]["totalDrops"] += newDrops
            self.accountData[accountName]["sessionDrops"] += newDrops
            self.saveTotalDrops(accountName)
            if lastDropleague:
                self.accountData[accountName]["lastDrop"] = datetime.now().strftime("%H:%M:%S %d/%m") + f' ({lastDropleague})'
            else:
                self.accountData[accountName]["lastDrop"] = datetime.now().strftime("%H:%M:%S %d/%m")

    def loadTotalDrops(self, accountName: str):
        try:
            with open(f"./sessions/{accountName}.json", "r") as f:
                saveData = json.load(f)
                totalDrops = saveData["totalDrops"]
        except (FileNotFoundError, KeyError):
            totalDrops = 0

        return totalDrops

    def saveTotalDrops(self, accountName: str):

        totalDrops = {
            "totalDrops": self.accountData[accountName]["totalDrops"],
        }

        with open(f"./sessions/{accountName}.json", "w") as f:
            json.dump(totalDrops, f)

    def updateStatus(self, accountName: str, msg: str):
        self.accountData[accountName]["status"] = msg
    
    def updateLastDropCheck(self, accountName: str, lastDropCheck: int):
        self.accountData[accountName]["lastDropCheck"] = lastDropCheck

    def getLastDropCheck(self, accountName: str) -> int:
        return self.accountData[accountName]["lastDropCheck"]

    def addLoginFailed(self, accountName: str):
        self.accountData[accountName]["failedLoginCounter"] += 1

    def resetLoginFailed(self, accountName: str):
        self.accountData[accountName]["failedLoginCounter"] = 0
    
    def getFailedLogins(self, accountName: str):
        return self.accountData[accountName]["failedLoginCounter"]
    
