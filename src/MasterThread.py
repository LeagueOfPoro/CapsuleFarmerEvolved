from threading import Lock, Thread

from DataProviderThread import DataProviderThread
from FarmThread import FarmThread
from Restarter import Restarter
from SharedData import SharedData
from GuiConsoleThread import GuiConsoleThread


class MasterThread(Thread):
    def __init__(self, log, config, stats):
        super().__init__()
        self.stats = stats
        self.log = log
        self.config = config

    def run(self):
        farmThreads = {}
        refreshLock = Lock()
        locks = {"refreshLock": refreshLock}
        sharedData = SharedData()
        for account in self.config.accounts:
            self.stats.initNewAccount(account)
        restarter = Restarter(self.stats)

        self.log.info(f"Starting a GUI thread.")
        guiThread = GuiConsoleThread(self.log, self.config, self.stats, locks)
        guiThread.daemon = True
        guiThread.start()

        dataProviderThread = DataProviderThread(self.log, self.config, sharedData)
        dataProviderThread.daemon = True
        dataProviderThread.start()

        while True:
            for account in self.config.accounts:
                if account not in farmThreads and restarter.canRestart(account):
                    self.log.info(f"Starting a thread for {account}.")
                    thread = FarmThread(self.log, self.config, account, self.stats, locks, sharedData)
                    thread.daemon = True
                    thread.start()
                    farmThreads[account] = thread
                    self.log.info(f"Thread for {account} was created.")    

            toDelete = []
            for account in farmThreads:
                if farmThreads[account].is_alive():
                    farmThreads[account].join(1)
                else:
                    toDelete.append(account)
                    restarter.setRestartDelay(account)
                    self.stats.updateStatus(account, f"[red]ERROR - restart at {restarter.getNextStart(account).strftime('%H:%M:%S')}, failed logins: {stats.getFailedLogins(account)}")
                    self.log.warning(f"Thread {account} has finished and will restart at {restarter.getNextStart(account).strftime('%H:%M:%S')}. Number of consecutively failed logins: {stats.getFailedLogins(account)}")
            for account in toDelete:
                del farmThreads[account]
