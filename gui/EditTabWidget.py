from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtCore import pyqtSignal
from gui.CodeEdit import CodeEdit
import sys

class EditTabWidget(QTabWidget):
    tabsChanged = pyqtSignal()

    def __init__(self,env):
        super().__init__()
        self.env = env
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.tabCloseClicked)
        self.currentChanged.connect(self.tabChange)
        self.tabs = []

    def createTab(self,title,focus=False):
        textEdit = CodeEdit(self.env,isNew=True)
        
        tabid = self.addTab(textEdit,title)
        textEdit.tabid = tabid
        textEdit.modificationStateChange(False)
        tabcontent = []
        tabcontent.append(textEdit)
        tabcontent.append("")
        self.tabs.append(tabcontent)

        if focus:
            self.setCurrentIndex(tabid)

        self.tabsChanged.emit()

    def tabChange(self, tabid):
        try:
            self.tabs[self.currentIndex()][0].updateEolMenu()
            self.env.mainWindow.pathLabel.setText(self.tabs[self.currentIndex()][1])
            cursor = self.tabs[self.currentIndex()][0].textCursor()
            self.env.mainWindow.cursorPosLabel.setText(self.env.translate("mainWindow.statusBar.cursorPosLabel") % ((cursor.blockNumber() + 1), (cursor.columnNumber() + 1)) )
        except Exception as e:
            pass

    def tabCloseClicked(self,tabid):
        if self.tabs[tabid][0].isModified() and self.env.settings.saveClose:
            self.env.closeSaveWindow.openWindow(tabid)
        else:
            del self.tabs[tabid]
            self.removeTab(tabid)
            if len(self.tabs) == 0:
                sys.exit(0)
        for count, i in enumerate(self.tabs):
            i[0].tabid = count
        self.tabsChanged.emit()
