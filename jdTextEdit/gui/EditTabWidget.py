from PyQt6.QtWidgets import QTabWidget, QMenu, QInputDialog
from PyQt6.QtCore import pyqtSignal, Qt, QCoreApplication
from jdTextEdit.gui.EditContainer import EditContainer
from PyQt6.QtGui import QIcon, QContextMenuEvent, QAction
from typing import cast, Optional, TYPE_CHECKING
import traceback
import sys
import os


if TYPE_CHECKING:
    from jdTextEdit.gui.SplitViewWidget import SplitViewWidget

    from jdTextEdit.Environment import Environment
    from jdTextEdit.gui.CodeEdit import CodeEdit
    from jdTextEdit.Settings import Settings


class EditTabWidget(QTabWidget):
    tabsChanged = pyqtSignal()

    def __init__(self, env: "Environment", splitViewWidget: "SplitViewWidget", splitID: int) -> None:
        super().__init__()
        self.env = env
        self.splitViewWidget = splitViewWidget
        self.splitID = splitID
        self.tabCloseRequested.connect(self.tabCloseClicked)
        self.currentChanged.connect(self.tabChange)
        self.tabBarDoubleClicked.connect(self.tabDoubleClicked)

    def createTab(self, title: Optional[str] = None, focus: bool = False) -> None:
        """
        Creates a new tab with a edit container
        :param title: The title
        :param focus: Set to True if it should have focus at start
        """
        textEdit = EditContainer(self.env, self)

        tabid = self.addTab(textEdit, title or "")
        codeEdit = textEdit.getCodeEditWidget()
        codeEdit.tabid = tabid
        codeEdit.modificationStateChange(False)

        if focus:
            self.setCurrentIndex(tabid)
            if hasattr(self.env, "mainWindow"):
                self.splitViewWidget.getMainWindow().updateWindowTitle()

        self.tabsChanged.emit()
        self.env.tabWidgetSignals.tabCreated.emit(self, textEdit)

    def addExistingTab(self, container: EditContainer, title: str, icon: QIcon):
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

    def tabChange(self) -> None:
        try:
            currentEditWidget = self.editWidget(self.currentIndex())
        except Exception:
            return
        try:
            currentEditWidget.updateOtherWidgets()
        except Exception as ex:
            self.env.logger.exception(ex)

    def tabCloseClicked(self, tabid: int, notCloseProgram: bool = False, forceExit: bool = False) -> None:
        if self.editWidget(tabid).isModified() and self.env.settings.saveClose:
            try:
                self.env.closeSaveWindow.openWindow(tabid,self)
            except Exception as ex:
                self.env.logger.exception(ex)
        else:
            self.removeTab(tabid)
            if self.count() == 0:
                if self.splitViewWidget.splitterWidget.count() == 1 and not notCloseProgram:
                    if self.env.settings.get("exitLastTab") or forceExit:
                        self.env.mainWindow.saveDataClose()
                        sys.exit(0)
                    else:
                        self.createTab(QCoreApplication.translate("EditTabWidget", "Untitled"), focus=True)
                else:
                    #Delete widget from Splitter
                    self.close()
                    self.setParent(None)
                    self.splitViewWidget.updateTabWidgetID()
        self.tabsChanged.emit()
        self.env.tabWidgetSignals.tabClosed.emit(self)

    def tabDoubleClicked(self, tabid: int) -> None:
        if self.env.settings.tabDoubleClickClose:
            self.tabCloseClicked(tabid)

    def updateTabTitle(self, index: int) -> None:
        editWidget = self.editWidget(index)
        if editWidget.customTabName != "":
            self.setTabText(index, editWidget.customTabName)
        elif editWidget.filePath == "":
            self.setTabText(index, QCoreApplication.translate("EditTabWidget", "Untitled"))
        else:
            self.setTabText(index, os.path.basename(editWidget.filePath))

    def contextMenuEvent(self, event: QContextMenuEvent):
        index = self.tabBar().tabAt(event.pos())

        if index == -1:
            return

        codeEdit = self.widget(index).getCodeEditWidget()

        menu = QMenu(self)

        customTabNameSetAction = QAction(QCoreApplication.translate("EditTabWidget", "Set custom tab name"), self)
        customTabNameSetAction.triggered.connect(lambda: self.customTabNameSetClicked(index))
        menu.addAction(customTabNameSetAction)

        if codeEdit.customTabName != "":
            customTabNameRemoveAction = QAction(QCoreApplication.translate("EditTabWidget", "Remove custom tab name"), self)
            customTabNameRemoveAction.triggered.connect(lambda: self.customTabNameRemoveClicked(index))
            menu.addAction(customTabNameRemoveAction)

        menu.exec(event.globalPos())

    def customTabNameSetClicked(self, index: int):
        name = QInputDialog.getText(self, QCoreApplication.translate("EditTabWidget", "Enter name"), QCoreApplication.translate("EditTabWidget", "Please enter a custom name for this tab"))[0]

        if name == "":
            return

        self.widget(index).getCodeEditWidget().customTabName = name
        self.updateTabTitle(index)

    def customTabNameRemoveClicked(self, index: int):
        self.widget(index).getCodeEditWidget().customTabName = ""
        self.updateTabTitle(index)

    def updateSettings(self, settings: "Settings") -> None:
        if settings.get("tabBarPosition") == 0:
            self.setTabPosition(QTabWidget.TabPosition.North)
        elif settings.get("tabBarPosition") == 1:
            self.setTabPosition(QTabWidget.TabPosition.South)
        elif settings.get("tabBarPosition") == 2:
            self.setTabPosition(QTabWidget.TabPosition.West)
        elif settings.get("tabBarPosition") == 3:
            self.setTabPosition(QTabWidget.TabPosition.East)
        self.tabBar().setAutoHide(settings.get("hideTabBar"))
        self.setTabsClosable(settings.get("closeButtonTab"))
        self.setMovable(settings.get("allowTabMove"))

    def markWidgetAsActive(self) -> None:
        """
        This function is called from the focus event of CodeEdit
        """
        self.splitViewWidget.setActiveWidget(self.splitID)

    def setActive(self) -> None:
        """
        Sets the tab widget as active
        """
        #self.currentWidget().ensureCursorVisible()
        self.currentWidget().setFocus(Qt.FocusReason.OtherFocusReason)

    def getSessionData(self, currentID: int) -> tuple[dict, int]:
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

    def restoreSession(self, data: dict, old_version: bool = False):
        """
        Restores a session. This function should not be called outside restoreSession() of SpliViewWidget.
        :param data: The session data
        :param old_version: Sets to true if a session of a old version is loaded
        """
        if old_version:
            current_id = 0
        for count, i in enumerate(data["tabs"]):
            self.createTab("Place")
            editWidget = self.widget(count).getCodeEditWidget()
            if old_version:
                f = open(os.path.join(self.env.dataDir, "session_data", str(current_id)), "rb")
                current_id += 1
            else:
                f = open(os.path.join(self.env.dataDir, "session_data", str(i["id"])), "rb")
            text = f.read().decode(i["encoding"], errors="replace")
            editWidget.setText(text)
            f.close()
            editWidget.restoreSaveMetaData(i)
            self.updateTabTitle(count)
        self.setCurrentIndex(data["selectedTab"])

    def getSplitViewWidget(self) -> "SplitViewWidget":
        return self.splitViewWidget

    def containerWidget(self, index: int) -> EditContainer:
        """
        Same as widgets(), but casts it to EditContainer
        """
        return cast(EditContainer, self.widget(index))

    def editWidget(self, index: int) -> "CodeEdit":
        """
        Returns the CodeEdit widget for this index
        """
        return self.containerWidget(index).getCodeEditWidget()
