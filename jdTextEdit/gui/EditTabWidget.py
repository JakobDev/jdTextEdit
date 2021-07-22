from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtCore import pyqtSignal, Qt
from jdTextEdit.gui.EditContainer import EditContainer
from PyQt6.QtGui import QIcon
import traceback
import sys
import os

class EditTabWidget(QTabWidget):
    tabsChanged = pyqtSignal()

    def __init__(self,env,splitViewWidget,splitID):
        super().__init__()
        self.env = env
        self.splitViewWidget = splitViewWidget
        self.splitID = splitID
        self.tabCloseRequested.connect(self.tabCloseClicked)
        self.currentChanged.connect(self.tabChange)
        self.tabBarDoubleClicked.connect(self.tabDoubleClicked)

    def createTab(self,title: str,focus=None):
        """
        Creates a new tab with a edit container
        :param title: The title
        :param focus: Set to True if it should have focus at start
        """
        textEdit = EditContainer(self.env,self)

        tabid = self.addTab(textEdit,title)
        codeEdit = textEdit.getCodeEditWidget()
        codeEdit.tabid = tabid
        codeEdit.modificationStateChange(False)

        if focus:
            self.setCurrentIndex(tabid)
            if hasattr(self.env,"mainWindow"):
                self.env.mainWindow.updateWindowTitle()

        self.tabsChanged.emit()
        self.env.tabWidgetSignals.tabCreated.emit(self,textEdit)

    def addExistingTab(self,container: EditContainer, title: str, icon: QIcon):
        """
        Adds a existing EditContainer as tab
        :param container: The EditConatiner
        :param title: The title of the tab
        :param icon: The icon of the tab
        :return:
        """
        tabid = self.addTab(container, title)
        container.tabWidget = self
        codeEdit = container.getCodeEditWidget()
        codeEdit.tabid = tabid
        self.setTabIcon(tabid, icon)
        self.env.tabWidgetSignals.tabCreated.emit(self,container)

    def tabChange(self, tabid):
        try:
            currentEditWidget = self.widget(self.currentIndex()).getCodeEditWidget()
        except:
            return
        try:
            currentEditWidget.updateOtherWidgets()
        except Exception as e:
            pass
            #print(e)

    def tabCloseClicked(self,tabid,notCloseProgram=None,forceExit=None):
        if self.widget(tabid).getCodeEditWidget().isModified() and self.env.settings.saveClose:
            try:
                self.env.closeSaveWindow.openWindow(tabid,self)
            except Exception as e:
                print(traceback.format_exc(), end="")
        else:
            self.removeTab(tabid)
            if self.count() == 0:
                if self.splitViewWidget.splitterWidget.count() == 1 and not notCloseProgram:
                    if self.env.settings.exitLastTab or forceExit:
                        self.env.mainWindow.saveDataClose()
                        sys.exit(0)
                    else:
                        self.createTab(self.env.translate("mainWindow.newTabTitle"),focus=True)
                else:
                    #Delete widget from Splitter
                    self.close()
                    self.setParent(None)
                    self.splitViewWidget.updateTabWidgetID()
        self.tabsChanged.emit()
        self.env.tabWidgetSignals.tabClosed.emit(self)

    def tabDoubleClicked(self,tabid):
        if self.env.settings.tabDoubleClickClose:
            self.tabCloseClicked(tabid)

    def updateSettings(self, settings):
        if settings.tabBarPosition == 0:
            self.setTabPosition(QTabWidget.TabPosition.North)
        elif settings.tabBarPosition == 1:
            self.setTabPosition(QTabWidget.TabPosition.South)
        elif settings.tabBarPosition == 2:
            self.setTabPosition(QTabWidget.TabPosition.West)
        elif settings.tabBarPosition == 3:
            self.setTabPosition(QTabWidget.TabPosition.East)
        self.tabBar().setAutoHide(settings.hideTabBar)
        self.setTabsClosable(settings.closeButtonTab)
        self.setMovable(settings.allowTabMove)

    def markWidgetAsActive(self):
        """
        This function is called from the focus event of CodeEdit
        """
        self.splitViewWidget.setActiveWidget(self.splitID)

    def setActive(self):
        """
        Sets the tab widget as active
        """
        #self.currentWidget().ensureCursorVisible()
        self.currentWidget().setFocus(Qt.FocusReason.OtherFocusReason)

    def getSessionData(self,currentID : int):
        """
        Returns all data for session.json and save all files hat are open. This function should not be called outside getSessionData() of SpliViewWidget.
        :param currentID: the current ID
        :return: data, currentID
        """
        data = {}
        data["selectedTab"] = self.currentIndex()
        data["tabs"] = []
        for i in range(self.count()):
            editWidget = self.widget(i).getCodeEditWidget()
            f = open(os.path.join(self.env.dataDir, "session_data", str(currentID)), "wb")
            f.write(editWidget.text().encode(editWidget.getUsedEncoding(), errors="replace"))
            f.close()
            editData = editWidget.getSaveMetaData()
            editData["id"] = currentID
            data["tabs"].append(editData)
            currentID += 1
        return data, currentID

    def restoreSession(self,data: dict, old_version: bool = False):
        """
        Restores a session. This function should not be called outside restoreSession() of SpliViewWidget.
        :param data: The session data
        :param old_version: Sets to true if a session of a old version is loaded
        """
        if old_version:
            current_id = 0
        for count, i in enumerate(data["tabs"]):
            if i["path"] == "":
                self.createTab(self.env.translate("mainWindow.newTabTitle"))
            else:
                self.createTab(os.path.basename(i["path"]))
            editWidget = self.widget(count).getCodeEditWidget()
            if old_version:
                f = open(os.path.join(self.env.dataDir, "session_data", str(current_id)), "rb")
                current_id += 1
            else:
                f = open(os.path.join(self.env.dataDir,"session_data",str(i["id"])), "rb")
            text = f.read().decode(i["encoding"], errors="replace")
            editWidget.setText(text)
            f.close()
            editWidget.restoreSaveMetaData(i)
        self.setCurrentIndex(data["selectedTab"])
