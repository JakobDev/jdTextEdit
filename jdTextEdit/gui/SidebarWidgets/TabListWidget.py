from jdTextEdit.api.SidebarWidgetBase import SidebarWidgetBase
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QListWidget
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.gui.EditTabWidget import EditTabWidget
    from jdTextEdit.Environment import Environment


class TabListWidget(QListWidget, SidebarWidgetBase):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env

        self.tabWidgetList: list["EditTabWidget"] = []
        self.updateTabList()
        #env.mainWindow.getTabWidget().tabsChanged.connect(self.updateTabList)
        self.env.tabWidgetSignals.tabCreated.connect(lambda a,b: self.updateTabList())
        self.env.tabWidgetSignals.tabClosed.connect(lambda a: self.updateTabList())
        self.currentRowChanged.connect(self.changeTab)

    def updateTabList(self) -> None:
        self.clear()
        self.tabWidgetList.clear()
        for tabWidget in self.env.mainWindow.splitViewWidget.getAllTabWidgets():
            for i in range(tabWidget.count()):
                self.addItem(tabWidget.tabText(i))
                self.tabWidgetList.append(tabWidget)

    def changeTab(self, row: int) -> None:
        if row != -1:
            self.tabWidgetList[row].setCurrentIndex(row)

    def getName(self) -> str:
        return QCoreApplication.translate("TabListWidget", "Tabs")

    def getID(self) -> str:
        return "id"