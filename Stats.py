from datetime import datetime

class Stats:
    def __init__(self, farmThreads) -> None:
        self.farmThreads = farmThreads
        self.accountData = {}

    def initNewAccount(self, accountName: str):
        self.accountData[accountName] = {"lastCheck": "", "totalDrops": 0, "lastDrop": "", "liveMatches": "", "status": ""}
    
    def update(self, accountName: str, newDrops: int = 0, liveMatches: str = ""):
        self.accountData[accountName]["lastCheck"] = datetime.now().strftime("%H:%M:%S %d/%m")
        self.accountData[accountName]["liveMatches"] = liveMatches
        if newDrops > 0:
            self.accountData[accountName]["totalDrops"] += newDrops
            self.accountData[accountName]["lastDrop"] = datetime.now().strftime("%H:%M:%S %d/%m")
    
    def updateStatus(self, accountName: str, msg: str):
        self.accountData[accountName]["status"] = msg
    
