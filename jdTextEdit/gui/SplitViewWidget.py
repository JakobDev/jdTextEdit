from PyQt6.QtWidgets import QWidget, QSplitter, QHBoxLayout
from jdTextEdit.gui.EditTabWidget import EditTabWidget
from jdTextEdit.gui.CodeEdit import CodeEdit
from jdTextEdit.Enviroment import Enviroment
from typing import List

class SplitViewWidget(QWidget):
    def __init__(self,env: Enviroment):
        super().__init__()
        self.env = env
        self.activeID = 0

        self.splitterWidget = QSplitter(self)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.splitterWidget)

        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(mainLayout)

    def getCurrentTextEditWidget(self) -> CodeEdit:
        """
        Returns the current active edit widget
        :return: the widget
        """
        return self.splitterWidget.widget(self.activeID).currentWidget().getCodeEditWidget()

    def getCurrentTabWidget(self) -> EditTabWidget:
        """
        Returns the current active tab widget
        :return: the widget
        """
        return self.splitterWidget.widget(self.activeID)

    def getAllTabWidgets(self) -> List[EditTabWidget]:
        """
        Returns a list with tab widgets
        :return: lsi with widgets
        """
        widgetList = []
        for i in range(self.splitterWidget.count()):
            widgetList.append(self.splitterWidget.widget(i))
        return widgetList

    def setActiveWidget(self,splitID: int):
        """
        Sets the widget with the id as active
        """
        self.activeID = splitID

    def initTabWidget(self):
        """
        Starts the tab widget. This is called when jdTextEdit is started without a existing session.
        """
        self.splitterWidget.addWidget(EditTabWidget(self.env, self, 0))

    def splitVertical(self):
        """
        Splits vertical
        """
        tabWidget = EditTabWidget(self.env,self,self.splitterWidget.count())
        tabWidget.createTab(self.env.translate("mainWindow.newTabTitle"))
        tabWidget.updateSettings(self.env.settings)
        self.splitterWidget.insertWidget(self.activeID+1,tabWidget)
        self.env.mainWindow.deleteCurrentViewAction.setEnabled(True)

    def deleteCurrentView(self):
        """
        Deletes the current view
        """
        currentTabWidget = self.getCurrentTabWidget()
        widgetList = []
        for i in range(currentTabWidget.count()):
            widgetList.append({"widget": currentTabWidget.widget(i), "title": currentTabWidget.tabText(i), "icon": currentTabWidget.tabIcon(i)})
        currentTabWidget.setParent(None)
        self.activeID -= 1
        if self.activeID == -1:
            self.activeID = 0
        self.updateTabWidgetID()
        newTabWidget = self.getCurrentTabWidget()
        for i in widgetList:
            newTabWidget.addExistingTab(i["widget"], i["title"], i["icon"])
        if self.splitterWidget.count() == 1:
            self.env.mainWindow.deleteCurrentViewAction.setEnabled(False)

    def getSessionData(self) -> dict:
        """
        Returns all data that is needed for the session.json. This function should not be called outside saveSession() of MainWindow.
        :return: the data
        """
        count = 0
        data = {}
        data["tabWidgets"] = []
        for i in self.getAllTabWidgets():
            tabData, count = i.getSessionData(count)
            data["tabWidgets"].append(tabData)
        return data

    def restoreSession(self,data: dict):
        """
        Restores a session. This function should not be called outside restoreSession() of MainWindow.
        :param data: The session data
        """
        # Load session from older versions
        if "tabWidgets" not in data:
            self.splitterWidget.addWidget(EditTabWidget(self.env, self, self.splitterWidget.count()))
            self.splitterWidget.widget(self.splitterWidget.count() - 1).restoreSession(data, old_version=True)
            return
        for i in data["tabWidgets"]:
            self.splitterWidget.addWidget(EditTabWidget(self.env, self,self.splitterWidget.count()))
            self.splitterWidget.widget(self.splitterWidget.count()-1).restoreSession(i)
        if self.splitterWidget.count() > 1:
            self.env.mainWindow.deleteCurrentViewAction.setEnabled(True)

    def updateTabWidgetID(self):
        """
        Update the IDs of the TabWidgets. This is needed is a TabWidget is removed.
        """
        for count,i in enumerate(self.getAllTabWidgets()):
            i.splitID = count