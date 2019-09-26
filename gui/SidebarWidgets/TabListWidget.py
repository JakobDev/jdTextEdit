from PyQt5.QtWidgets import QListWidget

class TabListWidget(QListWidget):
    def __init__(self,env):
        super().__init__()
        self.env = env
        self.updateTabList()
        env.mainWindow.tabWidget.tabsChanged.connect(self.updateTabList)
        self.currentRowChanged.connect(self.changeTab)

    def updateTabList(self):
        self.clear()
        for i in range(self.env.mainWindow.tabWidget.count()):
            self.addItem(self.env.mainWindow.tabWidget.tabText(i))

    def changeTab(self, row):
        if row != -1:
            self.env.mainWindow.tabWidget.setCurrentIndex(row)
