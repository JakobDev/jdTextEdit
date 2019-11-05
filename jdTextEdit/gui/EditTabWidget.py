from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtCore import pyqtSignal
from jdTextEdit.gui.CodeEdit import CodeEdit
from PyQt5.Qsci import QsciMacro
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

    def createTab(self,title,focus=None):
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
            self.env.mainWindow.updateWindowTitle()

        self.tabsChanged.emit()

    def tabChange(self, tabid):
        currentEditWidget = self.widget(self.currentIndex())
        try:
            currentEditWidget.updateEolMenu()
            currentEditWidget.updateStatusBar()
            currentEditWidget.updateMenuActions()
            self.env.mainWindow.updateWindowTitle()
            if self.env.mainWindow.currentMacro:
                self.env.mainWindow.stopMacroRecording()
                macro = self.env.mainWindow.currentMacro.save()
                self.env.mainWindow.currentMacro = QsciMacro(currentEditWidget)
                self.env.mainWindow.currentMacro.load(macro)
        except Exception as e:
            pass
            #print(e)

    def tabCloseClicked(self,tabid,notCloseProgram=None):
        if self.tabs[tabid][0].isModified() and self.env.settings.saveClose:
            self.env.closeSaveWindow.openWindow(tabid)
        else:
            del self.tabs[tabid]
            self.removeTab(tabid)
            if len(self.tabs) == 0 and not notCloseProgram:
                sys.exit(0)
        for count, i in enumerate(self.tabs):
            i[0].tabid = count
        self.tabsChanged.emit()
