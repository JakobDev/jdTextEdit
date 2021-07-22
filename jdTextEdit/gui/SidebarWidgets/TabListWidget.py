from jdTextEdit.api.SidebarWidgetBase import SidebarWidgetBase
from PyQt6.QtWidgets import QListWidget

class TabListWidget(QListWidget,SidebarWidgetBase):
    def __init__(self,env):
        super().__init__()
        self.env = env
        self.tabWidgetList = []
        self.updateTabList()
        #env.mainWindow.getTabWidget().tabsChanged.connect(self.updateTabList)
        self.env.tabWidgetSignals.tabCreated.connect(lambda a,b: self.updateTabList())
        self.env.tabWidgetSignals.tabClosed.connect(lambda a: self.updateTabList())
        self.currentRowChanged.connect(self.changeTab)

    def updateTabList(self):
        self.clear()
        self.tabWidgetList.clear()
        for tabWidget in self.env.mainWindow.splitViewWidget.getAllTabWidgets():
            for i in range(tabWidget.count()):
                self.addItem(tabWidget.tabText(i))
                self.tabWidgetList.append(tabWidget)

    def changeTab(self, row):
        if row != -1:
            self.tabWidgetList[row].setCurrentIndex(row)

    def getName(self) -> str:
        return self.env.translate("sidebar.tabs")

    def getID(self) -> str:
        return "id"