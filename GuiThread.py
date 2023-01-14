from threading import Thread
from time import sleep
from rich.live import Live
from rich.table import Table


class GuiThread(Thread):
    """
    A thread that creates a capsule farm for a given account
    """

    def __init__(self, log, config, stats):
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
    
    def generateTable(self):
        table = Table()
        table.add_column("Account")
        table.add_column("Status")
        table.add_column("Live matches")
        table.add_column("Last check")
        # table.add_column("Last drop")
        # table.add_column("Drops")

        for acc in self.stats.accountData:
            if acc not in self.stats.farmThreads :
                status = "[yellow]WAIT"
            else:
                status = self.stats.accountData[acc]["status"] if self.stats.farmThreads[acc].is_alive() else "[red]ERROR"
            # table.add_row(f"{acc}", f"{status}", f"{self.stats.accountData[acc]['liveMatches']}", f"{self.stats.accountData[acc]['lastCheck']}", f"{self.stats.accountData[acc]['lastDrop']}", f"{self.stats.accountData[acc]['totalDrops']}")
            table.add_row(f"{acc}", f"{status}", f"{self.stats.accountData[acc]['liveMatches']}", f"{self.stats.accountData[acc]['lastCheck']}")
        return table

    def run(self):
        """
        Report the status of all accounts
        """
        with Live(self.generateTable(), refresh_per_second=1) as live:
            while True:
                live.update(self.generateTable())
                sleep(1)
                
    def stop(self):
        """
        Try to stop gracefully
        """
        pass