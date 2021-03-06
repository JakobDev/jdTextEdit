from PyQt5.QtWidgets import QListWidget

class TabListWidget(QListWidget):
    def __init__(self,env):
        super().__init__()
        self.env = env
        self.updateTabList()
        #env.mainWindow.getTabWidget().tabsChanged.connect(self.updateTabList)
        self.currentRowChanged.connect(self.changeTab)

    def updateTabList(self):
        self.clear()
        for tabWidget in self.env.mainWindow.splitViewWidget.getAllTabWidgets():
            for i in range(tabWidget.count()):
                self.addItem(tabWidget.tabText(i))

    def changeTab(self, row):
        if row != -1:
            self.env.mainWindow.getTabWidget().setCurrentIndex(row)
