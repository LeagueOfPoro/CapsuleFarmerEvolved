from threading import Thread
from time import sleep
from rich.live import Live
from rich.table import Table


class GuiThread(Thread):
    """
    A thread that creates a capsule farm for a given account
    """

    def __init__(self, log, config, stats, locks):
        """
        Initializes the FarmThread

        :param log: Logger object
        :param config: Config object
        :param stats: Stats, Stats object
        """
        super().__init__()
        self.log = log
        self.config = config
        self.stats = stats
        self.locks = locks
    
    def generateTable(self):
        table = Table()
        table.add_column("Account")
        table.add_column("Status")
        table.add_column("Live matches")
        table.add_column("Heartbeat")
        table.add_column("Last drop")
        table.add_column("League")
        table.add_column("Drops")

        for acc in self.stats.accountData:
            status = self.stats.accountData[acc]["status"]
            table.add_row(f"{acc}", f"{status}", f"{self.stats.accountData[acc]['liveMatches']}", f"{self.stats.accountData[acc]['lastCheck']}", f"{self.stats.accountData[acc]['lastDrop']}",f"{self.stats.accountData[acc]['lastDropLeague']}", f"{self.stats.accountData[acc]['totalDrops']}")
            # table.add_row(f"{acc}", f"{status}", f"{self.stats.accountData[acc]['liveMatches']}", f"{self.stats.accountData[acc]['lastCheck']}")
        return table

    def run(self):
        """
        Report the status of all accounts
        """
        with Live(self.generateTable(), auto_refresh=False) as live:
            while True:
                live.update(self.generateTable())
                sleep(1)
                self.locks["refreshLock"].acquire()
                live.refresh()
                self.locks["refreshLock"].release()
                
    def stop(self):
        """
        Try to stop gracefully
        """
        pass