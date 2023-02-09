from datetime import datetime, timedelta


class Restarter:
    def __init__(self, accountStats) -> None:
        self.stats = accountStats
        self.startTimes = {acc: datetime.now()
                           for acc in accountStats.accountData}

    def setRestartDelay(self, accountName: str):
        """
        Get the earliest time of the next thread restart based on the number of failed logins

        :param accountName: string, name of the account 
        """
        failedLogins = self.stats.getFailedLogins(accountName)

        # do not use match-case to maintain compatibility with Python 3.9
        delay = 0
        if failedLogins == 1:
            delay = 10
        elif failedLogins == 2:
            delay = 30
        elif failedLogins == 3:
            delay = 150
        elif failedLogins == 4:
            delay = 300
        elif failedLogins == 5:
            delay = 600
        elif failedLogins >= 6:
            delay = 1800
        self.startTimes[accountName] = datetime.now() + \
            timedelta(seconds=delay)

    def getNextStart(self, accountName: str) -> datetime:
        return self.startTimes[accountName]

    def canRestart(self, accountName: str) -> bool:
        return self.getNextStart(accountName) < datetime.now()
