from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtCore import pyqtSignal
from jdTextEdit.gui.EditContainer import EditContainer
from PyQt5.Qsci import QsciMacro
import sys

class EditTabWidget(QTabWidget):
    tabsChanged = pyqtSignal()

    def __init__(self,env):
        super().__init__()
        self.env = env
        self.setMovable(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.tabCloseClicked)
        self.currentChanged.connect(self.tabChange)
        #self.tabs = []

    def createTab(self,title,focus=None):
        textEdit = EditContainer(self.env)
        
        tabid = self.addTab(textEdit,title)
        codeEdit = textEdit.getCodeEditWidget()
        codeEdit.tabid = tabid
        codeEdit.modificationStateChange(False)

        if focus:
            self.setCurrentIndex(tabid)
            if hasattr(self.env,"mainWindow"):
                self.env.mainWindow.updateWindowTitle()

        self.tabsChanged.emit()

    def tabChange(self, tabid):
        try:
            currentEditWidget = self.widget(self.currentIndex()).getCodeEditWidget()
        except:
            return
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

    def tabCloseClicked(self,tabid,notCloseProgram=None,forceExit=None):
        if self.widget(tabid).getCodeEditWidget().isModified() and self.env.settings.saveClose:
            self.env.closeSaveWindow.openWindow(tabid)
        else:
            self.removeTab(tabid)
            if self.count() == 0 and not notCloseProgram:
                if self.env.settings.exitLastTab or forceExit:
                    self.env.mainWindow.saveDataClose()
                    sys.exit(0)
                else:
                    self.createTab(self.env.translate("mainWindow.newTabTitle"),focus=True)
        self.tabsChanged.emit()
