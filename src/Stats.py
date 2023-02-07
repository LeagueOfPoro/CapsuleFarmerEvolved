from datetime import datetime
from Notifications import NotificationManager

class Stats:
    def __init__(self, farmThreads) -> None:
        self.farmThreads = farmThreads
        self.accountData = {}

    def initNewAccount(self, accountName: str):
        self.accountData[accountName] = {"lastCheck": "", "totalDrops": 0, "lastDrop": "N/A", "liveMatches": "", "status": "[yellow]WAIT", "failedLoginCounter": 0, "lastDropCheck": int(datetime.now().timestamp()*1e3)}
    
    def update(self, notificationManager: NotificationManager, accountName: str, newDrops: int = 0, liveMatches: str = ""):
        self.accountData[accountName]["lastCheck"] = datetime.now().strftime("%H:%M:%S %d/%m")
        self.accountData[accountName]["liveMatches"] = liveMatches
        if newDrops > 0:
            notificationManager.makeNotificationDrop((accountName),"{} New Drop(s) received".format(newDrops))
            self.accountData[accountName]["totalDrops"] += newDrops
            self.accountData[accountName]["lastDrop"] = datetime.now().strftime("%H:%M:%S %d/%m")
    
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
    
