from functools import partial
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.clock import Clock
from MasterThread import MasterThread
from Stats import Stats
from kivy.core.window import Window
import threading


class GuiThread(MDApp):
    def __init__(self, stats, **kwargs):
        super().__init__(**kwargs)
        self.stats = stats
        print(self.stats.accountData)

    def build(self):
        window_sizes=Window.size
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        # self.stats.initNewAccount("Account 1")
        # self.stats.update("Account 1", 0, "", "")
        # self.stats.update("Account 1", 0, str(window_sizes), "")
        # Clock.schedule_interval(self.update_data, 1)
        rowData = []
        for acc in self.stats.accountData:
            rowData.append((acc, self.stats.accountData[acc]['status'], self.stats.accountData[acc]['liveMatches'], self.stats.accountData[acc]['lastCheck'], self.stats.accountData[acc]['lastDrop'], self.stats.accountData[acc]['totalDrops']))
        layout = AnchorLayout()
        self.dataTable = MDDataTable(
            size_hint=(0.95, 0.6),
            column_data=[
                ("Account", dp(20)),
                ("Status", dp(30)),
                ("Live matches", dp(50)),
                ("Heartbeat", dp(30)),
                ("Last drop", dp(30)),
                ("Drops", dp(30)),
            ],
            
            row_data=rowData,
        )
        layout.add_widget(self.dataTable)
        Clock.schedule_interval(partial(self.updateData, self), 1)
        return layout
    
    def updateData(self, *largs):
        rowData = []
        for acc in self.stats.accountData:
            rowData.append((acc, self.stats.accountData[acc]['status'], self.stats.accountData[acc]['liveMatches'], self.stats.accountData[acc]['lastCheck'], self.stats.accountData[acc]['lastDrop'], self.stats.accountData[acc]['totalDrops']))
        self.dataTable.update_row_data(self.dataTable, rowData)
