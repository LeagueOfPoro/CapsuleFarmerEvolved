from threading import Thread
from time import sleep, strftime, localtime

from VersionManager import VersionManager

from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.console import Console

class GuiThread(Thread):
    """
    A thread that creates a capsule farm for a given account
    """

    def __init__(self, log, config, stats, locks, currentVersion):
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
        self.currentVersion = currentVersion
        self.startedTime = strftime('%b %d, %H:%M', localtime())
    
    def generateTable(self):
        vm = VersionManager()

        accountsKeyValues = {"Status": "status",
                             "Heartbeat": "lastCheck",
                             "Last drop": "lastDrop",
                             "Session Drops": "sessionDrops",
                             "Lifetime Drops": "totalDrops",
                             "Live Matches": "liveMatches"}

        infoTable = Table()
        infoLayout = Layout(infoTable, name="info", size=8)

        infoTable.add_column(f"Capsule Farmer Evolved v{self.currentVersion}")
        infoTable.add_row("[steel_blue1]Please consider supporting League of Poro on YouTube.[/]")
        infoTable.add_row("If you need help with the app, join our Discord.")
        infoTable.add_row("https://discord.gg/ebm5MJNvHU")
        infoTable.add_row(f"Started: [green]{strftime(self.startedTime)}[/]")

        updateTable = Table()
        updateLayout = Layout(updateTable, name="update", size=5)
        if not vm.isLatestVersion(self.currentVersion):
            updateTable.add_column(f"NEW VERSION AVAILABLE v{vm.getLatestTag()}")
            updateTable.add_row(f"Download it from: https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/releases/latest")

        accountsTable = Table()
        accountsLayout = Layout(accountsTable, name="accounts", size=10)
        accountsTable.add_column("Accounts", width=15)
        for acc in self.stats.accountData:
            accountsTable.add_column(f"{acc}")

        rows = []
        for key, value in accountsKeyValues.items():
            if value == "totalDrops" and not self.config.showHistoricalDrops:
                continue
            row = [key]
            for acc in self.stats.accountData:
                if value == "liveMatches":
                    if len(self.stats.accountData[acc][value]) == 0:
                        row.append("0")
                    else:
                        row.append(str(len(self.stats.accountData[acc][value].split(", "))))
                else:
                    row.append(str(self.stats.accountData[acc][value]))
            rows.append(row)

        for row in rows:
            accountsTable.add_row(*row)

        matches = set()
        for acc in self.stats.accountData:
            if len(self.stats.accountData[acc]["liveMatches"]) == 0:
                continue
            if len(self.stats.accountData[acc]["liveMatches"]) == 1:
                matches.add(self.stats.accountData[acc]["liveMatches"][0])
                continue
            liveMatches = self.stats.accountData[acc]["liveMatches"].split(", ")
            for match in liveMatches:
                if match not in matches:
                    matches.add(match)

        matchesTable = Table()
        matchesLayout = Layout(matchesTable, name="matches")
        matchesTable.add_column(f"Live Matches", width=15)
        for acc in self.stats.accountData:
            matchesTable.add_column("", width=len(acc))

        for match in matches:
            row = [match]
            for acc in self.stats.accountData:
                if match in self.stats.accountData[acc]["liveMatches"]:
                    row.append("[green]OK[/]")
                else:
                    row.append("[red]Error[/]")
            matchesTable.add_row(*row, end_section=True)

        if not vm.isLatestVersion(self.currentVersion):
            tables = [infoLayout, updateLayout, accountsLayout, matchesLayout]
        else:
            tables = [infoLayout, accountsLayout, matchesLayout]

        return tables

    def generateLayout(self):
        tablesWithLayouts = self.generateTable()
        layout = Layout()

        layout.split(*tablesWithLayouts)

        return layout

    def run(self):
        """
        Report the status of all accounts
        """
        console = Console(force_terminal=True)
        with Live(self.generateLayout(), auto_refresh=False, console=console) as live:
            while True:
                live.update(self.generateLayout())
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
