from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QApplication, QLabel, QFileDialog
from PyQt5.QtCore import Qt, QDir, QFileSystemWatcher
from PyQt5.QtGui import QKeySequence, QIcon, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from gui.DockWidget import DockWidget
from gui.EditTabWidget import EditTabWidget
from string import ascii_uppercase
from PyQt5.Qsci import QsciScintilla
from Functions import executeCommand, getThemeIcon, openFileDefault, showMessageBox
import tempfile
import shutil
import json
import sys
import os
import re

class MainWindow(QMainWindow):
    def __init__(self,env):
        super().__init__()
        self.env = env
        self.setupMenubar()
        self.tabWidget = EditTabWidget(env)
        self.setupStatusBar()
        if os.path.isfile(os.path.join(env.dataDir,"session.json")):
            self.restoreSession()
            if len(sys.argv) == 2:
                self.tabWidget.createTab("",focus=True)
                self.openFile(os.path.abspath(sys.argv[1]))
        else:
            self.tabWidget.createTab(env.translate("mainWindow.newTabTitle"))
            if len(sys.argv) == 2:
                self.openFile(os.path.abspath(sys.argv[1]))
        self.toolbar = self.addToolBar("toolbar")
        self.toolbar.addAction(self.env.menuActions["newFile"])
        self.setCentralWidget(self.tabWidget)
        self.setWindowTitle("jdTextEdit")
        self.updateSettings(self.env.settings)
 
    def setup(self):
        #This is called, after all at least
        self.env.sidepane = DockWidget(self.env)
        self.env.sidepane.hide()
        self.addDockWidget(Qt.LeftDockWidgetArea,self.env.sidepane)
        for i in self.tabWidget.tabs:
            i[0].modificationStateChange(i[0].isModified())
        if self.env.settings.showSidepane:
            self.toggleSidebarClicked()
        self.env.sidepane.content.setCurrentWidget(self.env.settings.sidepaneWidget)
        self.getTextEditWidget().updateEolMenu()
        if self.env.settings.startupDayTip:
            self.env.dayTipWindow.openWindow()
        #f = open(os.path.join(tempfile.gettempdir(),"test.txt"),"w")
        #f.close()
        #openFileWatcher = QFileSystemWatcher()
        #openFileWatcher.addPath(os.path.join(tempfile.gettempdir(),"test.txt"))
        #print(openFileWatcher.files())
        #openFileWatcher.fileChanged.connect(lambda: print("gfghjhg"))#self.openFileChanged)

    def getTextEditWidget(self):
        return self.getSelectedTab()[0]

    def setupStatusBar(self):
        self.pathLabel = QLabel()
        self.cursorPosLabel = QLabel(self.env.translate("mainWindow.statusBar.cursorPosLabel") % (1,1))
        self.statusBar().addWidget(self.pathLabel)
        self.statusBar().addPermanentWidget(self.cursorPosLabel)

    def setupMenubar(self):
        self.menubar = self.menuBar()
        self.recentFilesMenu = QMenu(self.env.translate("mainWindow.menu.openRecent"))
        self.recentFilesMenu.setIcon(getThemeIcon(self.env,"document-open-recent"))

        filemenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.file"))
        
        new = QAction("&" + self.env.translate("mainWindow.menu.file.new"),self)
        new.setShortcut(QKeySequence.New)
        new.setIcon(getThemeIcon(self.env,"document-new"))
        new.triggered.connect(self.newMenuBarClicked)
        new.setData(["newFile"])
        filemenu.addAction(new)

        self.templateMenu = QMenu(self.env.translate("mainWindow.menu.newTemplate"),self)
        self.templateMenu.setIcon(getThemeIcon(self.env,"document-new"))
        self.updateTemplateMenu()
        filemenu.addMenu(self.templateMenu)
        
        filemenu.addSeparator()

        openmenu = QAction("&" + self.env.translate("mainWindow.menu.file.open"),self)
        openmenu.setShortcut(QKeySequence.Open)
        openmenu.setIcon(getThemeIcon(self.env,"document-open"))
        openmenu.triggered.connect(self.openMenuBarClicked)
        openmenu.setData(["fileOpen"])
        filemenu.addAction(openmenu)

        
        openDirectoryMenu = QAction(self.env.translate("mainWindow.menu.file.openDirectory"),self)
        openDirectoryMenu.setIcon(getThemeIcon(self.env,"folder-open"))
        openDirectoryMenu.triggered.connect(self.openDirectoryMenuBarClicked)
        openDirectoryMenu.setData(["directoryOpen"])
        filemenu.addAction(openDirectoryMenu)

        filemenu.addMenu(self.recentFilesMenu)

        filemenu.addSeparator()

        save = QAction("&" + self.env.translate("mainWindow.menu.file.save"),self)
        save.setShortcut(QKeySequence.Save)
        save.setIcon(getThemeIcon(self.env,"document-save"))
        save.triggered.connect(lambda: self.saveMenuBarClicked(self.tabWidget.currentIndex()))
        save.setData(["saveFile"])
        filemenu.addAction(save)

        saveAs = QAction("&" + self.env.translate("mainWindow.menu.file.saveAs"),self)
        saveAs.setShortcut(QKeySequence.SaveAs)
        saveAs.setIcon(getThemeIcon(self.env,"document-save-as"))
        saveAs.triggered.connect(lambda: self.saveAsMenuBarClicked(self.tabWidget.currentIndex()))
        saveAs.setData(["saveAsFile"])
        filemenu.addAction(saveAs)

        saveAll = QAction(self.env.translate("mainWindow.menu.file.saveAll"),self)
        saveAll.setShortcut("Shift+Alt+S")
        saveAll.setIcon(getThemeIcon(self.env,"document-save-all"))
        saveAll.triggered.connect(self.saveAllMenuBarClicked)
        saveAll.setData(["saveAll"])
        filemenu.addAction(saveAll)

        filemenu.addSeparator()

        closeTab = QAction(self.env.translate("mainWindow.menu.file.close"),self)
        closeTab.setShortcut(QKeySequence.Close)
        closeTab.setIcon(QIcon(os.path.join(self.env.programDir,"icons","document-close.png")))
        closeTab.triggered.connect(lambda: self.tabWidget.tabCloseClicked(self.tabWidget.currentIndex()))
        closeTab.setData(["closeTab"])
        filemenu.addAction(closeTab)

        printMenuItem = QAction("&" + self.env.translate("mainWindow.menu.file.print"),self)
        printMenuItem.setShortcut(QKeySequence.Print)
        printMenuItem.setIcon(getThemeIcon(self.env,"document-print"))
        printMenuItem.triggered.connect(self.printMenuBarClicked)
        printMenuItem.setData(["print"])
        filemenu.addAction(printMenuItem)

        exit = QAction("&" + self.env.translate("mainWindow.menu.file.exit"),self)
        exit.setShortcut(QKeySequence.Quit)
        exit.setIcon(getThemeIcon(self.env,"application-exit"))
        exit.triggered.connect(self.close)
        exit.setData(["exit"])
        filemenu.addAction(exit)
        
        editMenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.edit"))

        self.undoMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.undo"),self)
        self.undoMenubarItem.setShortcut(QKeySequence.Undo)
        self.undoMenubarItem.setIcon(getThemeIcon(self.env,"edit-undo"))
        self.undoMenubarItem.triggered.connect(lambda: self.getTextEditWidget().undo())
        self.undoMenubarItem.setData(["undo"])
        editMenu.addAction(self.undoMenubarItem)
        self.undoMenubarItem.setEnabled(False)

        self.redoMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.redo"),self)
        self.redoMenubarItem.setShortcut(QKeySequence.Redo)
        self.redoMenubarItem.setIcon(getThemeIcon(self.env,"edit-redo"))
        self.redoMenubarItem.triggered.connect(lambda: self.getTextEditWidget().redo())
        self.redoMenubarItem.setData(["redo"])
        editMenu.addAction(self.redoMenubarItem)
        self.redoMenubarItem.setEnabled(False)

        editMenu.addSeparator()

        self.cutMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.cut"),self)
        self.cutMenubarItem.setShortcut(QKeySequence.Cut)
        self.cutMenubarItem.setIcon(getThemeIcon(self.env,"edit-cut"))
        self.cutMenubarItem.triggered.connect(lambda: self.getTextEditWidget().cut())
        self.cutMenubarItem.setData(["cut"])
        editMenu.addAction(self.cutMenubarItem)
        self.cutMenubarItem.setEnabled(False)

        self.copyMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.copy"),self)
        self.copyMenubarItem.setShortcut(QKeySequence.Copy)
        self.copyMenubarItem.setIcon(getThemeIcon(self.env,"edit-copy"))
        self.copyMenubarItem.triggered.connect(lambda: self.getTextEditWidget().copy())
        self.copyMenubarItem.setData(["copy"])
        editMenu.addAction(self.copyMenubarItem)
        self.copyMenubarItem.setEnabled(False)

        paste = QAction("&" + self.env.translate("mainWindow.menu.edit.paste"),self)
        paste.setShortcut(QKeySequence.Paste)
        paste.setIcon(getThemeIcon(self.env,"edit-paste"))
        paste.triggered.connect(lambda: self.getTextEditWidget().paste())
        paste.setData(["paste"])
        editMenu.addAction(paste)

        self.deleteMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.delete"),self)
        self.deleteMenubarItem.setShortcut(QKeySequence.Delete)
        self.deleteMenubarItem.setIcon(getThemeIcon(self.env,"edit-delete"))
        self.deleteMenubarItem.triggered.connect(lambda: self.getTextEditWidget().removeSelectedText())
        self.deleteMenubarItem.setData(["delete"])
        editMenu.addAction(self.deleteMenubarItem)
        self.deleteMenubarItem.setEnabled(False)

        editMenu.addSeparator()

        selectAll = QAction("&" + self.env.translate("mainWindow.menu.edit.selectAll"),self)
        selectAll.setShortcut(QKeySequence.SelectAll)
        selectAll.setIcon(getThemeIcon(self.env,"edit-select-all"))
        selectAll.triggered.connect(lambda: self.getTextEditWidget().selectAll())
        selectAll.setData(["selectAll"])
        editMenu.addAction(selectAll)

        editMenu.addSeparator()
 
        clipboardCopyMenu = QMenu(self.env.translate("mainWindow.menu.edit.copyClipboard"),self)
        
        copyPath = QAction(self.env.translate("mainWindow.menu.edit.copyClipboard.copyPath"),self)
        copyPath.triggered.connect(lambda: self.env.clipboard.setText(self.getSelectedTab()[1]))
        copyPath.setData(["copyPath"])
        clipboardCopyMenu.addAction(copyPath)

        copyDirectory = QAction(self.env.translate("mainWindow.menu.edit.copyClipboard.copyDirectory"),self)
        copyDirectory.triggered.connect(lambda: self.env.clipboard.setText(os.path.dirname(self.getSelectedTab()[1])))
        copyDirectory.setData(["copyDirectory"])
        clipboardCopyMenu.addAction(copyDirectory)

        copyFilename = QAction(self.env.translate("mainWindow.menu.edit.copyClipboard.copyFilename"),self)
        copyFilename.triggered.connect(lambda: self.env.clipboard.setText(os.path.basename(self.getSelectedTab()[1])))
        copyFilename.setData(["copyFilename"])
        clipboardCopyMenu.addAction(copyFilename)

        editMenu.addMenu(clipboardCopyMenu)

        convertCase = QMenu(self.env.translate("mainWindow.menu.edit.convertCase"),self)

        convertUppercase = QAction(self.env.translate("mainWindow.menu.edit.convertCase.uppercase"),self)
        convertUppercase.triggered.connect(lambda: self.getTextEditWidget().replaceSelectedText(self.getTextEditWidget().selectedText().upper()))
        convertUppercase.setData(["convertUppercase"])
        convertCase.addAction(convertUppercase)

        convertLowercase = QAction(self.env.translate("mainWindow.menu.edit.convertCase.lowercase"),self)
        convertLowercase.triggered.connect(lambda: self.getTextEditWidget().replaceSelectedText(self.getTextEditWidget().selectedText().lower()))
        convertLowercase.setData(["convertLowercase"])
        convertCase.addAction(convertLowercase)

        convertTitle = QAction(self.env.translate("mainWindow.menu.edit.convertCase.title"),self)
        convertTitle.triggered.connect(lambda: self.getTextEditWidget().replaceSelectedText(self.getTextEditWidget().selectedText().title()))
        convertTitle.setData(["convertTitle"])
        convertCase.addAction(convertTitle)

        convertSwap = QAction(self.env.translate("mainWindow.menu.edit.convertCase.swap"),self)
        convertSwap.triggered.connect(lambda: self.getTextEditWidget().replaceSelectedText(self.getTextEditWidget().selectedText().swapcase()))
        convertSwap.setData(["convertSwap"])
        convertCase.addAction(convertSwap)

        editMenu.addMenu(convertCase)

        eolModeMenu = QMenu(self.env.translate("mainWindow.menu.edit.eol"),self)
    
        self.eolModeWindows = QAction("Windows",self)
        self.eolModeWindows.triggered.connect(lambda: self.getTextEditWidget().changeEolMode(QsciScintilla.EolWindows))
        self.eolModeWindows.setData(["eolModeWindows"])
        self.eolModeWindows.setCheckable(True)
        eolModeMenu.addAction(self.eolModeWindows)

        self.eolModeUnix = QAction("Unix",self)
        self.eolModeUnix.triggered.connect(lambda: self.getTextEditWidget().changeEolMode(QsciScintilla.EolUnix))
        self.eolModeUnix.setData(["eolModeWindows"])
        self.eolModeUnix.setCheckable(True)
        eolModeMenu.addAction(self.eolModeUnix)

        self.eolModeMac = QAction("Mac",self)
        self.eolModeMac.triggered.connect(lambda: self.getTextEditWidget().changeEolMode(QsciScintilla.EolMac))
        self.eolModeMac.setData(["eolModeUnix"])
        self.eolModeMac.setCheckable(True)
        eolModeMenu.addAction(self.eolModeMac)

        editMenu.addMenu(eolModeMenu)
        editMenu.addSeparator()

        settings = QAction("&" + self.env.translate("mainWindow.menu.edit.settings"),self)
        settings.setShortcut(QKeySequence.Preferences)
        settings.setIcon(getThemeIcon(self.env,"preferences-other"))
        settings.triggered.connect(lambda: self.env.settingsWindow.openWindow())
        settings.setData(["settings"])
        editMenu.addAction(settings)

        viewMenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.view"))

        zoomMenu = QMenu(self.env.translate("mainWindow.menu.view.zoom"),self)
        
        zoomIn = QAction(self.env.translate("mainWindow.menu.view.zoom.zoomIn"),self)
        zoomIn.setShortcut(QKeySequence.ZoomIn)
        zoomIn.triggered.connect(lambda: self.getTextEditWidget().zoomIn())
        zoomIn.setData(["zoomIn"])
        zoomMenu.addAction(zoomIn)

        zoomOut = QAction(self.env.translate("mainWindow.menu.view.zoom.zoomOut"),self)
        zoomOut.setShortcut(QKeySequence.ZoomOut)
        zoomOut.triggered.connect(lambda: self.getTextEditWidget().zoomOut())
        zoomOut.setData(["zoomOut"])
        zoomMenu.addAction(zoomOut)

        zoomMenu.addSeparator()

        zoom100 = QAction("100%",self)
        zoom100.triggered.connect(lambda: self.getTextEditWidget().zoomTo(1))
        zoom100.setData(["zoom100"])
        zoomMenu.addAction(zoom100)

        viewMenu.addMenu(zoomMenu)

        fullscreen = QAction(self.env.translate("mainWindow.menu.view.fullscreen"),self)
        fullscreen.setShortcut(QKeySequence.FullScreen)
        fullscreen.triggered.connect(self.fullscreenMenuBarClicked)
        fullscreen.setData(["fullscreen"])
        fullscreen.setCheckable(True)
        viewMenu.addAction(fullscreen)
        
        self.toggleSidebarAction = QAction(self.env.translate("mainWindow.menu.view.sidebar"),self)
        self.toggleSidebarAction.triggered.connect(self.toggleSidebarClicked)
        self.toggleSidebarAction.setData(["toggleSidebar"])
        self.toggleSidebarAction.setCheckable(True)
        viewMenu.addAction(self.toggleSidebarAction)

        searchmenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.search"))

        search = QAction("&" + self.env.translate("mainWindow.menu.search.search"),self)
        search.setShortcut(QKeySequence.Find)
        search.setIcon(getThemeIcon(self.env,"edit-find"))
        search.triggered.connect(lambda: self.env.searchWindow.openWindow(self.getTextEditWidget()))
        search.setData(["find"])
        searchmenu.addAction(search)
        
        searchAndReplace = QAction("&" + self.env.translate("mainWindow.menu.search.searchAndReplace"),self)
        searchAndReplace.setShortcut(QKeySequence.Replace)
        searchAndReplace.setIcon(getThemeIcon(self.env,"edit-find-replace"))
        searchAndReplace.triggered.connect(self.searchAndReplaceMenuBarClicked)
        searchAndReplace.setData(["findReplaceWindow"])
        searchmenu.addAction(searchAndReplace)
        
        gotoLine = QAction(self.env.translate("mainWindow.menu.search.gotoLine"),self)
        gotoLine.setShortcut("Ctrl+L")
        gotoLine.triggered.connect(lambda: self.env.gotoLineWindow.openWindow(self.getTextEditWidget()))
        gotoLine.setData(["gotoLine"])
        searchmenu.addAction(gotoLine)

        toolsMenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.tools"))

        pickColor = QAction(self.env.translate("mainWindow.menu.tools.pickColor"),self)
        pickColor.triggered.connect(self.pickColorClicked)
        pickColor.setData(["pickColor"])
        toolsMenu.addAction(pickColor)

        documentStatistics = QAction("&" + self.env.translate("mainWindow.menu.tools.documentStatistics"),self)
        documentStatistics.triggered.connect(lambda: self.env.documentStatistics.openWindow(self.getTextEditWidget()))
        documentStatistics.setData(["documentStatistics"])
        toolsMenu.addAction(documentStatistics)

        insertDateTime = QAction("&" + self.env.translate("mainWindow.menu.tools.insertDateTime"),self)
        insertDateTime.triggered.connect(lambda: self.env.dateTimeWindow.openWindow(self.getTextEditWidget()))
        insertDateTime.setData(["insertDateTime"])
        toolsMenu.addAction(insertDateTime)

        self.languageMenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.language"))

        self.updateLanguageMenu()

        self.executeMenu = self.menubar.addMenu(self.env.translate("mainWindow.menu.execute"))
        self.updateExecuteMenu()
        
        aboutMenu = self.menubar.addMenu("&?")

        openDataFolder = QAction(self.env.translate("mainWindow.menu.about.openDataDir"),self)
        openDataFolder.triggered.connect(lambda: openFileDefault(self.env.dataDir))
        openDataFolder.setData(["openDataFolder"])
        aboutMenu.addAction(openDataFolder)

        showDayTip = QAction(self.env.translate("mainWindow.menu.about.dayTip"),self)
        showDayTip.triggered.connect(lambda: self.env.dayTipWindow.openWindow())
        showDayTip.setData(["showDayTip"])
        aboutMenu.addAction(showDayTip)

        aboutMenu.addSeparator()

        about = QAction(self.env.translate("mainWindow.menu.about.about"),self)
        about.triggered.connect(lambda: self.env.aboutWindow.show())
        about.setData(["about"])
        aboutMenu.addAction(about)
    
        aboutQt = QAction(self.env.translate("mainWindow.menu.about.aboutQt"),self)
        aboutQt.triggered.connect(QApplication.instance().aboutQt)
        aboutQt.setData(["aboutQt"])
        aboutMenu.addAction(aboutQt)

        self.updateRecentFilesMenu()
        self.getMenuActions(self.menubar)
        separator = QAction("Separator")
        separator.setData(["separator"])
        self.env.menuActions["separator"] = separator

    def updateToolbar(self, settings):
        self.toolbar.clear()
        for i in settings.toolBar:
            if i == "separator":
                self.toolbar.addSeparator()
            else:
                self.toolbar.addAction(self.env.menuActions[i])
                
    def getMenuActions(self, menu):
        for action in menu.actions():
            try:
                if isinstance(action.data()[0], str):
                    self.env.menuActions[action.data()[0]] = action
            except:
                pass
            if action.menu():
                self.getMenuActions(action.menu())

    def languageActionClicked(self):
        action = self.sender()
        if action:
            lexer = action.data()[0]()
            self.getTextEditWidget().setSyntaxHighlighter(lexer,lexerList=action.data())

    def languagePlainTextClicked(self):
        editWidget = self.getTextEditWidget()
        editWidget.setLexer(None)
        editWidget.currentLexer = None
        editWidget.updateSettings(self.env.settings)

    def updateTemplateMenu(self):
        self.templateMenu.clear()
        
        if len(self.env.templates) == 0:
            empty = QAction(self.env.translate("mainWindow.menu.newTemplate.empty"),self)
            empty.setEnabled(False)
            self.templateMenu.addAction(empty)
        else:
            for i in self.env.templates:
                templateAction = QAction(i[0],self)
                templateAction.setData([False,i[1]])
                templateAction.triggered.connect(self.openTemplate)
                self.templateMenu.addAction(templateAction)

    def openTemplate(self, sender):
        action = self.sender()
        if action:
            self.openFile(action.data()[1],template=True)
            self.getSelectedTab()[1] = ""
            self.pathLabel.setText("")
            
    def updateRecentFilesMenu(self):
        self.recentFilesMenu.clear()
        
        if len(self.env.recentFiles) == 0:
            empty = QAction(self.env.translate("mainWindow.menu.openRecent.empty"),self)
            empty.setEnabled(False)
            self.recentFilesMenu.addAction(empty)
        else:
            count = 1
            for i in self.env.recentFiles:
                fileItem = QAction(str(count) + ". " + i,self)
                fileItem.setData([False,i])
                fileItem.triggered.connect(self.openRecentFile)
                self.recentFilesMenu.addAction(fileItem)
                count += 1
            self.recentFilesMenu.addSeparator()
            clear = QAction(self.env.translate("mainWindow.menu.openRecent.clear"),self)
            clear.triggered.connect(self.clearRecentFiles)
            self.recentFilesMenu.addAction(clear)
            openAll = QAction(self.env.translate("mainWindow.menu.openRecent.openAll"),self)
            openAll.triggered.connect(self.openAllRecentFiles)
            self.recentFilesMenu.addAction(openAll)
        self.env.saveRecentFiles()
    
    def openRecentFile(self):
        action = self.sender()
        if action:
            self.openFile(action.data()[1])

    def clearRecentFiles(self):
        self.env.recentFiles = []
        self.updateRecentFilesMenu()

    def openAllRecentFiles(self):
        for i in self.env.recentFiles:
            self.openFile(i)

    def updateLanguageMenu(self):
        self.languageMenu.clear()
        alphabet = {}
        for i in self.env.lexerList:
            startLetter = i[1][0]
            if not startLetter in alphabet:
                alphabet[startLetter] = []
            alphabet[startLetter].append(i)
        for c in ascii_uppercase:
            if c in alphabet:
                letterMenu = QMenu(c,self)
                for i in alphabet[c]:
                    languageAction = QAction(i[1],self)
                    languageAction.setData(i)
                    languageAction.triggered.connect(self.languageActionClicked)
                    letterMenu.addAction(languageAction)
                self.languageMenu.addMenu(letterMenu)
        self.languageMenu.addSeparator()
        noneAction = QAction(self.env.translate("mainWindow.menu.language.plainText"),self)
        noneAction.triggered.connect(self.languagePlainTextClicked)
        self.languageMenu.addAction(noneAction)

    def updateExecuteMenu(self):
        self.executeMenu.clear()
        
        executeCommandMenu = QAction(self.env.translate("mainWindow.menu.execute.executeCommand"),self)
        executeCommandMenu.triggered.connect(lambda: self.env.executeCommandWindow.openWindow(self.getSelectedTab()))
        executeCommandMenu.setData(["executeCommand"])
        self.executeMenu.addAction(executeCommandMenu)

        if len(self.env.commands) != 0:
            self.executeMenu.addSeparator()
            for i in self.env.commands:
                command = QAction(i[0],self)
                command.setData([False,i[1],i[2]])
                command.triggered.connect(lambda sender: executeCommand(self.sender().data()[1],self.getSelectedTab(),self.sender().data()[2]))
                self.executeMenu.addAction(command)

        self.executeMenu.addSeparator()

        editCommands = QAction(self.env.translate("mainWindow.menu.execute.editCommands"),self)
        editCommands.triggered.connect(lambda: self.env.editCommandsWindow.openWindow())
        editCommands.setData(["editCommands"])
        self.executeMenu.addAction(editCommands)

    def openFile(self, path, template=False):
        for count, i in enumerate(self.tabWidget.tabs):
            if i[1] == path:
                self.tabWidget.setCurrentIndex(count)
                return
        if not os.path.isfile(path):
            return
        if not os.access(path,os.R_OK):
            showMessageBox(self.env.translate("noReadPermission.title"),self.env.translate("noReadPermission.text") % path)
            return
        filehandle = open(path,"rb")
        fileContent = filehandle.read().decode()
        if not self.getTextEditWidget().isNew:
            self.tabWidget.createTab(self.env.translate("mainWindow.newTabTitle"),focus=True)
        self.getTextEditWidget().setText(fileContent)
        self.getTextEditWidget().setModified(False)
        filehandle.close()
        self.getSelectedTab()[1] = path
        self.tabWidget.setTabText(self.tabWidget.currentIndex(),os.path.basename(path))
        self.tabWidget.tabsChanged.emit()
        self.pathLabel.setText(path)
        firstLine = fileContent.splitlines(True)[0]
        if firstLine.endswith("\r\n"):
            self.getTextEditWidget().setEolMode(QsciScintilla.EolWindows)
        elif firstLine.endswith("\n"):
            self.getTextEditWidget().setEolMode(QsciScintilla.EolUnix)
        elif firstLine.endswith("\r"):
            self.getTextEditWidget().setEolMode(QsciScintilla.EolMac)
        self.getTextEditWidget().updateEolMenu()
        if not template:
            count = 0
            for i in self.env.recentFiles:
                if i == path:
                    del self.env.recentFiles[count]
                count += 1
            self.env.recentFiles.insert(0,path)
            self.env.recentFiles = self.env.recentFiles[:self.env.settings.maxRecentFiles]
            self.updateRecentFilesMenu()
        try:
            part = path.split(".")
            fileType = part[len(part)-1]
            for i in self.env.lexerList:
                if i[2] == fileType:
                    lexer = i[0]()
                    self.getTextEditWidget().setSyntaxHighlighter(lexer,lexerList=i)
        except:
            pass

    def getSelectedTab(self):
        return self.tabWidget.tabs[self.tabWidget.currentIndex()]
    
    def newMenuBarClicked(self):
        self.tabWidget.createTab(self.env.translate("mainWindow.newTabTitle"),focus=True)
        
    
    def openMenuBarClicked(self):
        path = QFileDialog.getOpenFileName(self,self.env.translate("mainWindow.openFileDialog.title"))       
        if path[0]:
            self.openFile(path[0])

    def openDirectoryMenuBarClicked(self):
        path = QFileDialog.getExistingDirectory(self,self.env.translate("mainWindow.openDirectoryDialog.title"))
        if path:
            fileList = os.listdir(path)
            for i in fileList:
                filePath = os.path.join(path,i)
                if os.path.isfile(filePath):
                    self.openFile(filePath)

    def saveMenuBarClicked(self,tabid):
        if self.tabWidget.tabs[tabid][1] == "":
            self.saveAsMenuBarClicked(tabid)
        else:
            if not os.access(self.tabWidget.tabs[tabid][1],os.W_OK):
                showMessageBox(self.env.translate("noWritePermission.title"),self.env.translate("noWritePermission.text") % self.tabWidget.tabs[tabid][1])
                return
            filehandle = open(self.tabWidget.tabs[tabid][1],"w")
            filehandle.write(self.tabWidget.tabs[tabid][0].text())
            filehandle.close()
            self.getTextEditWidget().setModified(False)

    def deleteMenuBarClicked(self):
        lastText = self.env.clipboard.text()
        self.getTextEditWidget().cut()
        self.env.clipboard.setText(lastText)

    def saveAsMenuBarClicked(self,tabid):
        path = QFileDialog.getSaveFileName(self,self.env.translate("mainWindow.saveAsDialog.title"))
        
        if path[0]:
            if not os.access(path[0],os.W_OK):
                showMessageBox(self.env.translate("noWritePermission.title"),self.env.translate("noWritePermission.text") % path[0])
                return
            filehandle = open(path[0],"w")
            filehandle.write(self.tabWidget.tabs[tabid][0].text())
            filehandle.close()
            self.tabWidget.tabs[tabid][1] = path[0]
            self.tabWidget.setTabText(tabid,os.path.basename(path[0]))
            self.tabWidget.tabsChanged.emit()
            self.pathLabel.setText(path[0])
            self.getTextEditWidget().setModified(False)

    def saveAllMenuBarClicked(self):
        for i in range(len(self.tabWidget.tabs)):
            self.saveMenuBarClicked(i)

    def printMenuBarClicked(self):
        printer = QPrinter()  
        dialog  = QPrintDialog( printer);  
        dialog.setWindowTitle(self.env.translate("mainWindow.printDialog.title"));  
        if dialog.exec() == QDialog.Accepted:  
            #self.getTextEditWidget().document().print(printer);  
            #printer.printRange(self)
            document = QTextDocument()
            document.setPlainText(self.getTextEditWidget().text())
            document.print(printer)
 
    def fullscreenMenuBarClicked(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def searchAndReplaceMenuBarClicked(self):
        self.env.searchReplaceWindow.display(self.getSelectedTab()[0])

    def pickColorClicked(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.getTextEditWidget().insertText(col.name())

    def toggleSidebarClicked(self):
        if self.env.sidepane.enabled:
            self.env.sidepane.enabled = False
            self.env.sidepane.hide()
        else:
            self.env.sidepane.enabled = True
            self.env.sidepane.show()
        self.toggleSidebarAction.setChecked(self.env.sidepane.enabled)
            
    def updateSettings(self, settings):
        self.tabWidget.tabBar().setAutoHide(settings.hideTabBar)
        self.env.recentFiles = self.env.recentFiles[:self.env.settings.maxRecentFiles]
        self.updateRecentFilesMenu()
        self.updateToolbar(settings)
        if settings.showToolbar:
            self.toolbar.show()
        else:
            self.toolbar.close()

    def openFileChanged(self, path):
        print(path)

    def restoreSession(self):
        with open(os.path.join(self.env.dataDir,"session.json")) as f:
            data = json.load(f)
        for count, i in enumerate(data["tabs"]):
            if i[0] == "":
                self.tabWidget.createTab(self.env.translate("mainWindow.newTabTitle"))
            else:
                self.tabWidget.createTab(os.path.basename(i[0]))
                self.tabWidget.tabs[count][1] = i[0]
            f = open(os.path.join(self.env.dataDir,"session_data",str(count)),"r")
            self.tabWidget.tabs[count][0].setText(f.read())
            f.close()
            self.tabWidget.tabs[count][0].setModified(i[1])
            for l in self.env.lexerList:
                s = l[0]()
                if s.language() == i[2]:
                    self.tabWidget.tabs[count][0].setSyntaxHighlighter(s,lexerList=l)
        self.tabWidget.setCurrentIndex(data["selectedTab"])
        os.remove(os.path.join(self.env.dataDir,"session.json"))
        shutil.rmtree(os.path.join(self.env.dataDir,"session_data"))
            
    def closeEvent(self, event):
        self.env.settings.showSidepane = self.env.sidepane.enabled
        self.env.settings.sidepaneWidget = self.env.sidepane.content.getSelectedWidget()
        self.env.settings.save(os.path.join(self.env.dataDir,"settings.json"))
        if self.env.settings.saveSession:
            if not os.path.isdir(os.path.join(self.env.dataDir,"session_data")):
                os.mkdir(os.path.join(self.env.dataDir,"session_data"))
            data = {}
            data["selectedTab"] = self.tabWidget.currentIndex()
            data["tabs"] = []
            for count, i in enumerate(self.tabWidget.tabs):
                f = open(os.path.join(self.env.dataDir,"session_data",str(count)),"w")
                f.write(i[0].text())
                f.close()
                if i[0].currentLexer:
                    syntax = i[0].currentLexer.language()
                else:
                    syntax = ""
                data["tabs"].append([i[1],i[0].isModified(),syntax])
            with open(os.path.join(self.env.dataDir,"session.json"), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            sys.exit(0)
        else:
            for i in range(self.tabWidget.count()-1,-1,-1):
                self.tabWidget.tabCloseClicked(i)
            event.ignore()
                
