from threading import Thread
from time import sleep
from rich.live import Live
from rich.table import Table
from rich.console import Console
import sys
import os

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

        self.terminal_size = os.get_terminal_size()
    
    def generateTable(self):
        table = Table()
        table.add_column("Account")
        table.add_column("Status")
        table.add_column("Live matches")
        table.add_column("Heartbeat")
        table.add_column("Last drop")
        table.add_column("Session Drops")
        if self.config.showHistoricalDrops:
            table.add_column("Lifetime Drops")

        for acc in self.stats.accountData:
            status = self.stats.accountData[acc]["status"]
            if self.config.showHistoricalDrops:
                table.add_row(f"{acc}", f"{status}", f"{self.stats.accountData[acc]['liveMatches']}", f"{self.stats.accountData[acc]['lastCheck']}", f"{self.stats.accountData[acc]['lastDrop']}", f"{self.stats.accountData[acc]['sessionDrops']}", f"{self.stats.accountData[acc]['totalDrops']}")
            else:
                table.add_row(f"{acc}", f"{status}", f"{self.stats.accountData[acc]['liveMatches']}", f"{self.stats.accountData[acc]['lastCheck']}", f"{self.stats.accountData[acc]['lastDrop']}", f"{self.stats.accountData[acc]['sessionDrops']}")

        return table

    def update_terminal(self, old_terminal_size):
        # Check for terminal Size and clear the Screen if it changed in width
        new_terminal_size = os.get_terminal_size()

        # There's a bug where os.get_terminal_size() returns None
        if old_terminal_size is None:
            return new_terminal_size

        if new_terminal_size[0] != old_terminal_size[0]:
            # Check weather the operating system is windows or something else to clear the screen accordingly
            if sys.platform.startswith('win'):
                os.system('cls')
            else:
                os.system('clear')
            
            # update terminal_size to new_terminal_size
            return new_terminal_size

    def run(self):
        """
        Report the status of all accounts
        """
        console = Console(force_terminal=True)
        with Live(self.generateTable(), auto_refresh=False, console=console) as live:
            while True:
                if self.config.clearConsoleWhenResized:
                    self.terminal_size = self.update_terminal(self.terminal_size)
                
                live.update(self.generateTable())
                sleep(1)
                self.locks["refreshLock"].acquire()
                live.refresh()
                if self.locks["refreshLock"].locked():
                    self.locks["refreshLock"].release()
                
    def stop(self):
        """
        Try to stop gracefully
        """
        pass
