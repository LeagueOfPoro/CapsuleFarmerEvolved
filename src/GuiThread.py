import re
from functools import partial

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import sp
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable


class GuiThread(MDApp):
    def __init__(self, stats, **kwargs):
        super().__init__(**kwargs)
        self.stats = stats
        print(self.stats.accountData)

    def build(self):
        window_sizes = Window.size
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        layout = AnchorLayout()
        self.dataTable = MDDataTable(
            # size_hint=(0.95, 0.6),
            column_data=[
                ("Account", sp(20)),
                ("Status", sp(20)),
                ("Live matches", sp(50)),
                ("Heartbeat", sp(20)),
                ("Last drop", sp(23)),
                ("Drops", sp(10)),
            ],

            row_data=self.__getRowData(),
        )
        layout.add_widget(self.dataTable)
        Clock.schedule_interval(partial(self.updateData, self), 3)
        return layout

    def updateData(self, *largs):
        
        self.dataTable.update_row_data(self.dataTable, self.__getRowData())

    def __getRowData(self) -> list:
        rowData = []
        for acc in self.stats.accountData:
            status = re.sub(r'^.*?\]', "", self.stats.accountData[acc]['status'])
            rowData.append((acc,
                            status,
                            self.stats.accountData[acc]['liveMatches'],
                            self.stats.accountData[acc]['lastCheck'],
                            self.stats.accountData[acc]['lastDrop'],
                            self.stats.accountData[acc]['totalDrops']))
        return rowData


