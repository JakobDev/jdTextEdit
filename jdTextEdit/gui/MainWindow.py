from PyQt6.QtWidgets import QMainWindow, QMenu, QApplication, QLabel, QFileDialog, QStyleFactory, QDialog, QColorDialog, QInputDialog, QMessageBox
from PyQt6.Qsci import QsciScintilla, QsciScintillaBase, QsciMacro, QsciPrinter
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtPrintSupport import QPrintDialog
from PyQt6.QtCore import Qt, QFileSystemWatcher, QTimer, QCoreApplication
from jdTextEdit.Functions import executeCommand, getThemeIcon, openFileDefault, showMessageBox, saveWindowState, restoreWindowState, getTempOpenFilePath, isFilenameValid, saveProjects
from jdTextEdit.gui.EditTabWidget import EditTabWidget
from jdTextEdit.gui.SplitViewWidget import SplitViewWidget
from jdTextEdit.EncodingList import getEncodingList
from jdTextEdit.gui.DockWidget import DockWidget
from jdTextEdit.Updater import searchForUpdates
from jdTextEdit.gui.BannerWidgets.WrongEncodingBanner import WrongEncodingBanner
from jdTextEdit.gui.BannerWidgets.WrongEolBanner import WrongEolBanner
from jdTextEdit.gui.BannerWidgets.BigFileBanner import BigFileBanner
from jdTextEdit.gui.CodeEdit import CodeEdit
from jdTextEdit.Settings import Settings
from jdTextEdit.Enviroment import Enviroment
from string import ascii_uppercase
from typing import List
import webbrowser
import traceback
import random
import shutil
import atexit
import json
import sys
import os


class MainWindow(QMainWindow):
    def __init__(self, env: Enviroment):
        super().__init__()
        self.env = env
        self.currentMacro = None
        self.setupMenubar()
        self.splitViewWidget = SplitViewWidget(env)
        self.setupStatusBar()
        self.toolbar = self.addToolBar("toolbar")
        self.setCentralWidget(self.splitViewWidget)
        self.autoSaveTimer = QTimer()
        #self.autoSaveTimer.setInterval(2147483647)
        self.autoSaveTimer.timeout.connect(self.autoSaveTimeout)
        if "MainWindow" in env.windowState:
            restoreWindowState(self,env.windowState,"MainWindow")
        else:
            self.setGeometry(0, 0, 800, 600)

    def setup(self):
        #This is called, after all at least
        if os.path.isfile(os.path.join(self.env.dataDir,"session.json")) and not self.env.args["disableSessionRestore"]:
            try:
                self.restoreSession()
            except Exception as e:
                print(traceback.format_exc(),end="",file=sys.stderr)
                showMessageBox("Error","Could not restore session. This might be happen after an Update. If jdTextEdit crashes just restart it.")
                os.remove(os.path.join(self.env.dataDir,"session.json"))
                shutil.rmtree(os.path.join(self.env.dataDir,"session_data"))
                tabWidget = self.splitViewWidget.getCurrentTabWidget()
                if tabWidget.count() == 0:
                    tabWidget.createTab(self.env.translate("mainWindow.newTabTitle"))
        else:
            self.splitViewWidget.initTabWidget()
            self.splitViewWidget.getCurrentTabWidget().createTab(self.env.translate("mainWindow.newTabTitle"))
        self.updateLanguageMenu()
        if len(self.env.args["filename"]) == 1:
            self.openFileCommandline(os.path.abspath(self.env.args["filename"][0]))
        #self.getMenuActions(self.menubar)
        self.env.sidepane = DockWidget(self.env)
        self.env.sidepane.hide()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.env.sidepane)
        for tabWidget in self.splitViewWidget.getAllTabWidgets():
            for i in range(tabWidget.count()):
                widget = tabWidget.widget(i).getCodeEditWidget()
                widget.modificationStateChange(widget.isModified())
        if self.env.settings.showSidepane:
            self.toggleSidebarClicked()
        self.env.sidepane.content.setCurrentWidget(self.env.settings.sidepaneWidget)
        self.getTextEditWidget().updateEolMenu()
        self.getTextEditWidget().updateEncodingMenu()
        self.env.settingsWindow.setup()
        self.env.dayTipWindow.setup()
        self.updateSettings(self.env.settings)
        if self.env.settings.searchUpdates and self.env.enableUpdater:
            searchForUpdates(self.env, True)
        if self.env.settings.useIPC:
            open(getTempOpenFilePath(), "w").close()
            self.tempFileOpenWatcher = QFileSystemWatcher()
            self.tempFileOpenWatcher.addPath(getTempOpenFilePath())
            self.tempFileOpenWatcher.fileChanged.connect(self.openTempFileSignal)
            atexit.register(self.removeTempOpenFile)
        self.env.mainWindowSignals.windowInit.emit(self)
        self.show()
        #self.getTextEditWidget().ensureCursorVisible()
        if self.env.settings.startupDayTip:
            self.env.dayTipWindow.openWindow()

    def openFileCommandline(self, path: str):
        if os.path.isfile(path):
            self.openFile(path)
        else:
            #Check if the file is already open but do not exists anymore
            found = False
            for tabWidget in self.splitViewWidget.getAllTabWidgets():
                for i in range(tabWidget.count()):
                    if tabWidget.widget(i).getCodeEditWidget().getFilePath() == path:
                        tabWidget.setCurrentIndex(i)
                        found = True
            if not found:
                if os.path.isdir(path):
                    print("Can't open directory")
                else:
                    self.getTabWidget().createTab(os.path.basename(path),focus=True)
                    editWidget = self.getTextEditWidget()
                    editWidget.setFilePath(path)
                    editWidget.isNew = False
                    if self.env.settings.useEditorConfig:
                        editWidget.loadEditorConfig()

    def getTextEditWidget(self) -> CodeEdit:
        """
        Returns the current active edit widget
        :return: The edit widget
        """
        return self.splitViewWidget.getCurrentTextEditWidget()

    def getTabWidget(self) -> EditTabWidget:
        """
        Returns the current active tab widget
        :return: The tab widget
        """
        return self.splitViewWidget.getCurrentTabWidget()

    def openTempFileSignal(self,path: str):
        if os.path.getsize(path) == 0:
            return
        with open(path) as f:
            lines = f.read().splitlines()
        if lines[0] == "openFile":
            self.openFileCommandline(lines[1])
        open(path, "w").close()
        self.tempFileOpenWatcher.addPath(path)
        QApplication.setActiveWindow(self)

    def setupStatusBar(self):
        self.pathLabel = QLabel()
        self.cursorPosLabel = QLabel(self.env.translate("mainWindow.statusBar.cursorPosLabel") % (1,1))
        self.lexerLabel = QLabel()
        self.encodingLabel = QLabel()
        self.eolLabel = QLabel()
        self.statusBar().addWidget(self.pathLabel)
        self.statusBar().addPermanentWidget(self.eolLabel)
        self.statusBar().addPermanentWidget(self.encodingLabel)
        self.statusBar().addPermanentWidget(self.lexerLabel)
        self.statusBar().addPermanentWidget(self.cursorPosLabel)

    def setupMenubar(self):
        """
        Creates the Menubar with all Actions
        """
        self.menubar = self.menuBar()
        self.recentFilesMenu = QMenu(self.env.translate("mainWindow.menu.openRecent"))
        self.recentFilesMenu.setIcon(getThemeIcon(self.env,"document-open-recent"))

        self.filemenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.file"))

        new = QAction("&" + self.env.translate("mainWindow.menu.file.new"),self)
        new.setIcon(getThemeIcon(self.env,"document-new"))
        new.triggered.connect(self.newMenuBarClicked)
        new.setData(["newFile"])
        self.filemenu.addAction(new)
        self.env.pluginAPI.addAction(new)

        self.templateMenu = QMenu(self.env.translate("mainWindow.menu.file.newTemplate"),self)
        self.templateMenu.setIcon(getThemeIcon(self.env,"document-new"))
        self.updateTemplateMenu()
        self.filemenu.addMenu(self.templateMenu)

        self.filemenu.addSeparator()

        openmenu = QAction("&" + self.env.translate("mainWindow.menu.file.open"),self)
        openmenu.setIcon(getThemeIcon(self.env,"document-open"))
        openmenu.triggered.connect(self.openMenuBarClicked)
        openmenu.setData(["openFile"])
        self.filemenu.addAction(openmenu)
        self.env.pluginAPI.addAction(openmenu)

        openDirectoryMenu = QAction(self.env.translate("mainWindow.menu.file.openDirectory"),self)
        openDirectoryMenu.setIcon(getThemeIcon(self.env,"folder-open"))
        openDirectoryMenu.triggered.connect(self.openDirectoryMenuBarClicked)
        openDirectoryMenu.setData(["directoryOpen"])
        self.filemenu.addAction(openDirectoryMenu)
        self.env.pluginAPI.addAction(openDirectoryMenu)

        self.filemenu.addMenu(self.recentFilesMenu)

        self.filemenu.addSeparator()

        save = QAction("&" + self.env.translate("mainWindow.menu.file.save"),self)
        save.setIcon(getThemeIcon(self.env,"document-save"))
        save.triggered.connect(lambda: self.saveMenuBarClicked(self.getTextEditWidget()))
        save.setData(["saveFile"])
        self.filemenu.addAction(save)
        self.env.pluginAPI.addAction(save)

        saveAs = QAction("&" + self.env.translate("mainWindow.menu.file.saveAs"),self)
        saveAs.setIcon(getThemeIcon(self.env,"document-save-as"))
        saveAs.triggered.connect(lambda: self.saveAsMenuBarClicked(self.getTextEditWidget()))
        saveAs.setData(["saveAsFile"])
        self.filemenu.addAction(saveAs)
        self.env.pluginAPI.addAction(saveAs)

        saveAll = QAction(self.env.translate("mainWindow.menu.file.saveAll"),self)
        saveAll.setIcon(getThemeIcon(self.env,"document-save-all"))
        saveAll.triggered.connect(self.saveAllMenuBarClicked)
        saveAll.setData(["saveAll"])
        self.filemenu.addAction(saveAll)
        self.env.pluginAPI.addAction(saveAll)

        self.filemenu.addSeparator()

        closeTab = QAction(self.env.translate("mainWindow.menu.file.close"),self)
        closeTab.setIcon(QIcon(os.path.join(self.env.programDir,"icons","document-close.png")))
        closeTab.triggered.connect(lambda: self.getTabWidget().tabCloseClicked(self.getTabWidget().currentIndex()))
        closeTab.setData(["closeTab"])
        self.filemenu.addAction(closeTab)
        self.env.pluginAPI.addAction(closeTab)

        closeAllTabsAction = QAction(self.env.translate("mainWindow.menu.file.closeAllTabs"),self)
        closeAllTabsAction.setIcon(QIcon(os.path.join(self.env.programDir,"icons","document-close-all.png")))
        closeAllTabsAction.triggered.connect(self.closeAllTabs)
        closeAllTabsAction.setData(["closeAllTabs"])
        self.filemenu.addAction(closeAllTabsAction)
        self.env.pluginAPI.addAction(closeAllTabsAction)

        self.filemenu.addSeparator()

        printMenuItem = QAction("&" + self.env.translate("mainWindow.menu.file.print"),self)
        printMenuItem.setIcon(getThemeIcon(self.env,"document-print"))
        printMenuItem.triggered.connect(self.printMenuBarClicked)
        printMenuItem.setData(["print"])
        self.filemenu.addAction(printMenuItem)
        self.env.pluginAPI.addAction(printMenuItem)

        exit = QAction("&" + self.env.translate("mainWindow.menu.file.exit"),self)
        exit.setIcon(getThemeIcon(self.env,"application-exit"))
        exit.triggered.connect(self.close)
        exit.setData(["exit"])
        self.filemenu.addAction(exit)
        self.env.pluginAPI.addAction(exit)

        self.menubar.addMenu(self.filemenu)
        self.editMenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.edit"))

        self.undoMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.undo"),self)
        self.undoMenubarItem.setIcon(getThemeIcon(self.env,"edit-undo"))
        self.undoMenubarItem.triggered.connect(lambda: self.getTextEditWidget().undo())
        self.undoMenubarItem.setData(["undo"])
        self.editMenu.addAction(self.undoMenubarItem)
        self.env.pluginAPI.addAction(self.undoMenubarItem)
        self.undoMenubarItem.setEnabled(False)

        self.redoMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.redo"),self)
        self.redoMenubarItem.setIcon(getThemeIcon(self.env,"edit-redo"))
        self.redoMenubarItem.triggered.connect(lambda: self.getTextEditWidget().redo())
        self.redoMenubarItem.setData(["redo"])
        self.editMenu.addAction(self.redoMenubarItem)
        self.env.pluginAPI.addAction(self.redoMenubarItem)
        self.redoMenubarItem.setEnabled(False)

        self.editMenu.addSeparator()

        self.cutMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.cut"),self)
        self.cutMenubarItem.setIcon(getThemeIcon(self.env,"edit-cut"))
        self.cutMenubarItem.triggered.connect(lambda: self.getTextEditWidget().cut())
        self.cutMenubarItem.setData(["cut"])
        self.editMenu.addAction(self.cutMenubarItem)
        self.env.pluginAPI.addAction(self.cutMenubarItem)
        self.cutMenubarItem.setEnabled(False)

        self.copyMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.copy"),self)
        self.copyMenubarItem.setIcon(getThemeIcon(self.env,"edit-copy"))
        self.copyMenubarItem.triggered.connect(lambda: self.getTextEditWidget().copy())
        self.copyMenubarItem.setData(["copy"])
        self.editMenu.addAction(self.copyMenubarItem)
        self.env.pluginAPI.addAction(self.copyMenubarItem)
        self.copyMenubarItem.setEnabled(False)

        paste = QAction("&" + self.env.translate("mainWindow.menu.edit.paste"),self)
        paste.setIcon(getThemeIcon(self.env,"edit-paste"))
        paste.triggered.connect(lambda: self.getTextEditWidget().paste())
        paste.setData(["paste"])
        self.editMenu.addAction(paste)
        self.env.pluginAPI.addAction(paste)

        self.deleteMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.delete"),self)
        self.deleteMenubarItem.setIcon(getThemeIcon(self.env,"edit-delete"))
        self.deleteMenubarItem.triggered.connect(lambda: self.getTextEditWidget().removeSelectedText())
        self.deleteMenubarItem.setData(["delete"])
        self.editMenu.addAction(self.deleteMenubarItem)
        self.env.pluginAPI.addAction(self.deleteMenubarItem)
        self.deleteMenubarItem.setEnabled(False)

        self.editMenu.addSeparator()

        selectAll = QAction("&" + self.env.translate("mainWindow.menu.edit.selectAll"),self)
        selectAll.setIcon(getThemeIcon(self.env,"edit-select-all"))
        selectAll.triggered.connect(lambda: self.getTextEditWidget().selectAll())
        selectAll.setData(["selectAll"])
        self.editMenu.addAction(selectAll)
        self.env.pluginAPI.addAction(selectAll)

        self.editMenu.addSeparator()

        self.clipboardCopyMenu = QMenu(self.env.translate("mainWindow.menu.edit.copyClipboard"),self)

        copyPath = QAction(self.env.translate("mainWindow.menu.edit.copyClipboard.copyPath"),self)
        copyPath.triggered.connect(lambda: self.env.clipboard.setText(self.getTextEditWidget().getFilePath()))
        copyPath.setData(["copyPath"])
        self.clipboardCopyMenu.addAction(copyPath)
        self.env.pluginAPI.addAction(copyPath)

        copyDirectory = QAction(self.env.translate("mainWindow.menu.edit.copyClipboard.copyDirectory"),self)
        copyDirectory.triggered.connect(lambda: self.env.clipboard.setText(os.path.dirname(self.getTextEditWidget().getFilePath())))
        copyDirectory.setData(["copyDirectory"])
        self.clipboardCopyMenu.addAction(copyDirectory)
        self.env.pluginAPI.addAction(copyDirectory)

        copyFilename = QAction(self.env.translate("mainWindow.menu.edit.copyClipboard.copyFilename"),self)
        copyFilename.triggered.connect(lambda: self.env.clipboard.setText(os.path.basename(self.getTextEditWidget().getFilePath())))
        copyFilename.setData(["copyFilename"])
        self.clipboardCopyMenu.addAction(copyFilename)
        self.env.pluginAPI.addAction(copyFilename)

        copyUrlAction = QAction(self.env.translate("mainWindow.menu.edit.copyClipboard.copyURL"),self)
        copyUrlAction.triggered.connect(lambda: self.env.clipboard.setText("file://" + self.getTextEditWidget().getFilePath()))
        copyUrlAction.setData(["copyUrl"])
        self.clipboardCopyMenu.addAction(copyUrlAction)
        self.env.pluginAPI.addAction(copyUrlAction)

        self.editMenu.addMenu(self.clipboardCopyMenu)

        self.convertCase = QMenu(self.env.translate("mainWindow.menu.edit.convertCase"),self)

        convertUppercase = QAction(self.env.translate("mainWindow.menu.edit.convertCase.uppercase"),self)
        convertUppercase.triggered.connect(lambda: self.getTextEditWidget().replaceSelectedText(self.getTextEditWidget().selectedText().upper()))
        convertUppercase.setData(["convertUppercase"])
        self.convertCase.addAction(convertUppercase)
        self.env.pluginAPI.addAction(convertUppercase)

        convertLowercase = QAction(self.env.translate("mainWindow.menu.edit.convertCase.lowercase"),self)
        convertLowercase.triggered.connect(lambda: self.getTextEditWidget().replaceSelectedText(self.getTextEditWidget().selectedText().lower()))
        convertLowercase.setData(["convertLowercase"])
        self.convertCase.addAction(convertLowercase)
        self.env.pluginAPI.addAction(convertLowercase)

        convertTitle = QAction(self.env.translate("mainWindow.menu.edit.convertCase.title"),self)
        convertTitle.triggered.connect(lambda: self.getTextEditWidget().replaceSelectedText(self.getTextEditWidget().selectedText().title()))
        convertTitle.setData(["convertTitle"])
        self.convertCase.addAction(convertTitle)
        self.env.pluginAPI.addAction(convertTitle)

        convertSwap = QAction(self.env.translate("mainWindow.menu.edit.convertCase.swap"),self)
        convertSwap.triggered.connect(lambda: self.getTextEditWidget().replaceSelectedText(self.getTextEditWidget().selectedText().swapcase()))
        convertSwap.setData(["convertSwap"])
        self.convertCase.addAction(convertSwap)
        self.env.pluginAPI.addAction(convertSwap)

        self.editMenu.addMenu(self.convertCase)

        self.lineOperationsMenu = QMenu(self.env.translate("mainWindow.menu.edit.lineOperations"),self)

        duplicateCurrentLineAction = QAction(self.env.translate("mainWindow.menu.edit.lineOperations.duplicateCurrentLine"),self)
        duplicateCurrentLineAction.triggered.connect(self.duplicateCurrentLine)
        duplicateCurrentLineAction.setData(["duplicateCurrentLine"])
        self.lineOperationsMenu.addAction(duplicateCurrentLineAction)
        self.env.pluginAPI.addAction(duplicateCurrentLineAction)

        deleteCurrentLineAction = QAction(self.env.translate("mainWindow.menu.edit.lineOperations.deleteCurrentLine"),self)
        deleteCurrentLineAction.triggered.connect(self.removeCurrentLine)
        deleteCurrentLineAction.setData(["removeCurrentLine"])
        self.lineOperationsMenu.addAction(deleteCurrentLineAction)
        self.env.pluginAPI.addAction(deleteCurrentLineAction)

        sortAlphabetical = QAction(self.env.translate("mainWindow.menu.edit.lineOperations.sortAlphabetical"),self)
        sortAlphabetical.triggered.connect(self.sortLinesAlphabetical)
        sortAlphabetical.setData(["sortAlphabetical"])
        self.lineOperationsMenu.addAction(sortAlphabetical)
        self.env.pluginAPI.addAction(sortAlphabetical)

        shuffleLinesAction = QAction(self.env.translate("mainWindow.menu.edit.lineOperations.shuffleLines"),self)
        shuffleLinesAction.triggered.connect(self.shuffleLines)
        shuffleLinesAction.setData(["shuffleLines"])
        self.lineOperationsMenu.addAction(shuffleLinesAction)
        self.env.pluginAPI.addAction(shuffleLinesAction)

        self.editMenu.addMenu(self.lineOperationsMenu)

        self.eolModeMenu = QMenu(self.env.translate("mainWindow.menu.edit.eol"),self)

        self.eolModeWindows = QAction("Windows",self)
        self.eolModeWindows.triggered.connect(lambda: self.getTextEditWidget().changeEolMode(QsciScintilla.EolMode.EolWindows))
        self.eolModeWindows.setData(["eolModeWindows"])
        self.eolModeWindows.setCheckable(True)
        self.eolModeMenu.addAction(self.eolModeWindows)
        self.env.pluginAPI.addAction(self.eolModeWindows)

        self.eolModeUnix = QAction("Unix",self)
        self.eolModeUnix.triggered.connect(lambda: self.getTextEditWidget().changeEolMode(QsciScintilla.EolMode.EolUnix))
        self.eolModeUnix.setData(["eolModeWindows"])
        self.eolModeUnix.setCheckable(True)
        self.eolModeMenu.addAction(self.eolModeUnix)
        self.env.pluginAPI.addAction(self.eolModeUnix)

        self.eolModeMac = QAction("Mac",self)
        self.eolModeMac.triggered.connect(lambda: self.getTextEditWidget().changeEolMode(QsciScintilla.EolMode.EolMac))
        self.eolModeMac.setData(["eolModeUnix"])
        self.eolModeMac.setCheckable(True)
        self.eolModeMenu.addAction(self.eolModeMac)
        self.env.pluginAPI.addAction(self.eolModeMac)

        self.editMenu.addMenu(self.eolModeMenu)
        self.editMenu.addSeparator()

        settings = QAction("&" + self.env.translate("mainWindow.menu.edit.settings"),self)
        settings.setIcon(getThemeIcon(self.env,"preferences-other"))
        settings.triggered.connect(lambda: self.env.settingsWindow.openWindow())
        settings.setData(["settings"])
        self.editMenu.addAction(settings)
        self.env.pluginAPI.addAction(settings)

        self.viewMenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.view"))

        self.zoomMenu = QMenu(self.env.translate("mainWindow.menu.view.zoom"),self)

        zoomIn = QAction(self.env.translate("mainWindow.menu.view.zoom.zoomIn"),self)
        zoomIn.triggered.connect(lambda: self.getTextEditWidget().zoomIn())
        zoomIn.setData(["zoomIn"])
        self.zoomMenu.addAction(zoomIn)
        self.env.pluginAPI.addAction(zoomIn)

        zoomOut = QAction(self.env.translate("mainWindow.menu.view.zoom.zoomOut"),self)
        zoomOut.triggered.connect(lambda: self.getTextEditWidget().zoomOut())
        zoomOut.setData(["zoomOut"])
        self.zoomMenu.addAction(zoomOut)
        self.env.pluginAPI.addAction(zoomOut)

        self.zoomMenu.addSeparator()

        zoom0 = QAction("0%",self)
        zoom0.triggered.connect(lambda: self.getTextEditWidget().zoomTo(-10))
        zoom0.setData(["zoom0"])
        self.zoomMenu.addAction(zoom0)
        self.env.pluginAPI.addAction(zoom0)

        zoom50 = QAction("50%",self)
        zoom50.triggered.connect(lambda: self.getTextEditWidget().zoomTo(-5))
        zoom50.setData(["zoom50"])
        self.zoomMenu.addAction(zoom50)
        self.env.pluginAPI.addAction(zoom50)

        zoom100 = QAction("100%",self)
        zoom100.triggered.connect(lambda: self.getTextEditWidget().zoomTo(0))
        zoom100.setData(["zoom100"])
        self.zoomMenu.addAction(zoom100)
        self.env.pluginAPI.addAction(zoom100)

        zoom150 = QAction("150%",self)
        zoom150.triggered.connect(lambda: self.getTextEditWidget().zoomTo(5))
        zoom150.setData(["zoom150"])
        self.zoomMenu.addAction(zoom150)
        self.env.pluginAPI.addAction(zoom150)

        zoom200 = QAction("200%",self)
        zoom200.triggered.connect(lambda: self.getTextEditWidget().zoomTo(10))
        zoom200.setData(["zoom200"])
        self.zoomMenu.addAction(zoom200)
        self.env.pluginAPI.addAction(zoom200)

        zoom250 = QAction("250%",self)
        zoom250.triggered.connect(lambda: self.getTextEditWidget().zoomTo(15))
        zoom250.setData(["zoom250"])
        self.zoomMenu.addAction(zoom250)
        self.env.pluginAPI.addAction(zoom250)

        zoom300 = QAction("300%",self)
        zoom300.triggered.connect(lambda: self.getTextEditWidget().zoomTo(20))
        zoom300.setData(["zoom300"])
        self.zoomMenu.addAction(zoom300)
        self.env.pluginAPI.addAction(zoom300)

        self.zoomMenu.addSeparator()

        zoomDefault = QAction(self.env.translate("mainWindow.menu.view.zoom.zoomDefault"), self)
        zoomDefault.triggered.connect(lambda: self.getTextEditWidget().zoomTo(self.env.settings.defaultZoom))
        zoomDefault.setData(["zoomDefault"])
        self.zoomMenu.addAction(zoomDefault)
        self.env.pluginAPI.addAction(zoomDefault)

        zoomCustom = QAction(self.env.translate("mainWindow.menu.view.zoom.zoomCustom"), self)
        zoomCustom.triggered.connect(self.setCustomZoom)
        zoomCustom.setData(["zoomCustom"])
        self.zoomMenu.addAction(zoomCustom)
        self.env.pluginAPI.addAction(zoomCustom)

        self.viewMenu.addMenu(self.zoomMenu)

        self.fullscreenAction = QAction(self.env.translate("mainWindow.menu.view.fullscreen"), self)
        self.fullscreenAction.triggered.connect(self.fullscreenMenuBarClicked)
        self.fullscreenAction.setData(["fullscreen"])
        self.fullscreenAction.setCheckable(True)
        self.viewMenu.addAction(self.fullscreenAction)
        self.env.pluginAPI.addAction(self.fullscreenAction)

        self.toggleSidebarAction = QAction(self.env.translate("mainWindow.menu.view.sidebar"), self)
        self.toggleSidebarAction.triggered.connect(self.toggleSidebarClicked)
        self.toggleSidebarAction.setData(["toggleSidebar"])
        self.toggleSidebarAction.setCheckable(True)
        self.viewMenu.addAction(self.toggleSidebarAction)
        self.env.pluginAPI.addAction(self.toggleSidebarAction)

        self.viewMenu.addSeparator()

        foldAllAction = QAction(self.env.translate("mainWindow.menu.view.foldAll"),self)
        foldAllAction.triggered.connect(lambda: self.getTextEditWidget().SendScintilla(QsciScintillaBase.SCI_FOLDALL,0))
        foldAllAction.setData(["foldAll"])
        self.viewMenu.addAction(foldAllAction)
        self.env.pluginAPI.addAction(foldAllAction)

        unfoldAllAction = QAction(self.env.translate("mainWindow.menu.view.unfoldAll"),self)
        unfoldAllAction.triggered.connect(lambda: self.getTextEditWidget().SendScintilla(QsciScintillaBase.SCI_FOLDALL,1))
        unfoldAllAction.setData(["unfoldAll"])
        self.viewMenu.addAction(unfoldAllAction)
        self.env.pluginAPI.addAction(unfoldAllAction)

        self.viewMenu.addSeparator()

        self.splitViewMenu = QMenu(self.env.translate("mainWindow.menu.view.splitView"), self)

        splitVerticalAction = QAction(self.env.translate("mainWindow.menu.view.splitView.splitVertical"), self)
        splitVerticalAction.triggered.connect(lambda: self.splitViewWidget.splitVertical())
        splitVerticalAction.setData(["splitVertical"])
        self.splitViewMenu.addAction(splitVerticalAction)
        self.env.pluginAPI.addAction(splitVerticalAction)

        self.deleteCurrentViewAction = QAction(self.env.translate("mainWindow.menu.view.splitView.deleteCurrentView"), self)
        self.deleteCurrentViewAction.triggered.connect(lambda: self.splitViewWidget.deleteCurrentView())
        self.deleteCurrentViewAction.setData(["deleteCurrentView"])
        self.deleteCurrentViewAction.setEnabled(False)
        self.splitViewMenu.addAction(self.deleteCurrentViewAction)
        self.env.pluginAPI.addAction(self.deleteCurrentViewAction)

        self.viewMenu.addMenu(self.splitViewMenu)

        self.searchmenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.search"))

        search = QAction("&" + self.env.translate("mainWindow.menu.search.search"), self)
        search.setIcon(getThemeIcon(self.env,"edit-find"))
        search.triggered.connect(lambda: self.getTabWidget().currentWidget().showSearchBar())
        search.setData(["find"])
        self.searchmenu.addAction(search)
        self.env.pluginAPI.addAction(search)

        advancedSearch = QAction(self.env.translate("mainWindow.menu.search.advancedSearch"), self)
        advancedSearch.setIcon(getThemeIcon(self.env,"edit-find"))
        advancedSearch.triggered.connect(lambda: self.env.searchWindow.openWindow(self.getTextEditWidget()))
        self.searchmenu.addAction(advancedSearch)
        self.env.pluginAPI.addAction(advancedSearch)

        searchAndReplace = QAction("&" + self.env.translate("mainWindow.menu.search.searchAndReplace"), self)
        searchAndReplace.setIcon(getThemeIcon(self.env, "edit-find-replace"))
        searchAndReplace.triggered.connect(self.searchAndReplaceMenuBarClicked)
        searchAndReplace.setData(["findReplaceWindow"])
        self.searchmenu.addAction(searchAndReplace)
        self.env.pluginAPI.addAction(searchAndReplace)

        gotoLine = QAction(self.env.translate("mainWindow.menu.search.gotoLine"), self)
        gotoLine.triggered.connect(lambda: self.env.gotoLineWindow.openWindow(self.getTextEditWidget()))
        gotoLine.setData(["gotoLine"])
        self.searchmenu.addAction(gotoLine)
        self.env.pluginAPI.addAction(gotoLine)

        self.toolsMenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.tools"))

        pickColor = QAction(self.env.translate("mainWindow.menu.tools.pickColor"), self)
        pickColor.triggered.connect(self.pickColorClicked)
        pickColor.setData(["pickColor"])
        self.toolsMenu.addAction(pickColor)
        self.env.pluginAPI.addAction(pickColor)

        documentStatistics = QAction("&" + self.env.translate("mainWindow.menu.tools.documentStatistics"), self)
        documentStatistics.triggered.connect(lambda: self.env.documentStatistics.openWindow(self.getTextEditWidget()))
        documentStatistics.setData(["documentStatistics"])
        self.toolsMenu.addAction(documentStatistics)
        self.env.pluginAPI.addAction(documentStatistics)

        insertDateTime = QAction("&" + self.env.translate("mainWindow.menu.tools.insertDateTime"), self)
        insertDateTime.triggered.connect(lambda: self.env.dateTimeWindow.openWindow(self.getTextEditWidget()))
        insertDateTime.setData(["insertDateTime"])
        self.toolsMenu.addAction(insertDateTime)
        self.env.pluginAPI.addAction(insertDateTime)

        self.toolsMenu.addSeparator()

        stripSpacesAction = QAction(self.env.translate("mainWindow.menu.tools.stripSpaces"),self)
        stripSpacesAction.triggered.connect(self.stripSpaces)
        stripSpacesAction.setData(["stripSpaces"])
        self.toolsMenu.addAction(stripSpacesAction)
        self.env.pluginAPI.addAction(stripSpacesAction)

        replaceTabSpacesAction = QAction(self.env.translate("mainWindow.menu.tools.replaceTabSpaces"),self)
        replaceTabSpacesAction.triggered.connect(self.replaceTabSpaces)
        replaceTabSpacesAction.setData(["replaceTabSpaces"])
        self.toolsMenu.addAction(replaceTabSpacesAction)
        self.env.pluginAPI.addAction(replaceTabSpacesAction)

        replaceSpacesTabAction = QAction(self.env.translate("mainWindow.menu.tools.replaceSpacesTab"),self)
        replaceSpacesTabAction.triggered.connect(self.replaceSpacesTab)
        replaceSpacesTabAction.setData(["replaceSpacesTab"])
        self.toolsMenu.addAction(replaceSpacesTabAction)
        self.env.pluginAPI.addAction(replaceSpacesTabAction)

        self.toolsMenu.addSeparator()

        regExGrepAction = QAction(QCoreApplication.translate("MainWindow", "RegExGrep"))
        regExGrepAction.triggered.connect(lambda : self.env.regExGrepWindow.show())
        regExGrepAction.setData(["regExGrep"])
        self.toolsMenu.addAction(regExGrepAction)
        self.env.pluginAPI.addAction(regExGrepAction)

        self.languageMenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.language"))

        #self.updateLanguageMenu()

        self.encodingMenu = self.menubar.addMenu(self.env.translate("mainWindow.menu.encoding"))
        self.updateEncodingMenu()

        self.bookmarkMenu = self.menubar.addMenu(self.env.translate("mainWindow.menu.bookmarks"))

        addRemoveBookmarkAction = QAction(self.env.translate("mainWindow.menu.bookmarks.addRemoveBookmark"), self)
        addRemoveBookmarkAction.triggered.connect(self.addRemoveBookmark)
        addRemoveBookmarkAction.setData(["addRemoveBookmark"])
        self.bookmarkMenu.addAction(addRemoveBookmarkAction)
        self.env.pluginAPI.addAction(addRemoveBookmarkAction)

        nextBookmarkAction = QAction(self.env.translate("mainWindow.menu.bookmarks.nextBookmark"), self)
        nextBookmarkAction.triggered.connect(self.nextBookmark)
        nextBookmarkAction.setData(["nextBookmark"])
        self.bookmarkMenu.addAction(nextBookmarkAction)
        self.env.pluginAPI.addAction(nextBookmarkAction)

        previousBookmarkAction = QAction(self.env.translate("mainWindow.menu.bookmarks.previousBookmark"), self)
        previousBookmarkAction.triggered.connect(self.previousBookmark)
        previousBookmarkAction.setData(["previousBookmark"])
        self.bookmarkMenu.addAction(previousBookmarkAction)
        self.env.pluginAPI.addAction(previousBookmarkAction)

        clearBookmarksAction = QAction(self.env.translate("mainWindow.menu.bookmarks.clearBookmarks"), self)
        clearBookmarksAction.triggered.connect(self.clearBookmarks)
        clearBookmarksAction.setData(["clearBookmarks"])
        self.bookmarkMenu.addAction(clearBookmarksAction)
        self.env.pluginAPI.addAction(clearBookmarksAction)

        self.macroMenu = self.menubar.addMenu(self.env.translate("mainWindow.menu.macro"))

        self.recordMacroAction = QAction(self.env.translate("mainWindow.menu.macro.startRecording"), self)
        self.recordMacroAction.triggered.connect(self.startMacroRecording)
        self.recordMacroAction.setData(["recordMacro"])
        self.env.pluginAPI.addAction(self.recordMacroAction)

        self.stopMacroAction = QAction(self.env.translate("mainWindow.menu.macro.stopRecording"), self)
        self.stopMacroAction.triggered.connect(self.stopMacroRecording)
        self.stopMacroAction.setData(["stopMacro"])
        self.env.pluginAPI.addAction(self.stopMacroAction)
        self.stopMacroAction.setEnabled(False)

        self.playMacroAction = QAction(self.env.translate("mainWindow.menu.macro.playMacro"), self)
        self.playMacroAction.triggered.connect(self.playMacro)
        self.playMacroAction.setData(["playMacro"])
        self.env.pluginAPI.addAction(self.playMacroAction)
        self.playMacroAction.setEnabled(False)

        self.saveMacroAction = QAction(self.env.translate("mainWindow.menu.macro.saveMacro"), self)
        self.saveMacroAction.triggered.connect(self.saveMacro)
        self.saveMacroAction.setData(["saveMacro"])
        self.env.pluginAPI.addAction(self.saveMacroAction)
        self.saveMacroAction.setEnabled(False)

        self.manageMacrosAction = QAction(self.env.translate("mainWindow.menu.macro.manageMacros"), self)
        self.manageMacrosAction.triggered.connect(lambda: self.env.manageMacrosWindow.openWindow())
        self.manageMacrosAction.setData(["manageMacros"])
        self.env.pluginAPI.addAction(self.manageMacrosAction)

        self.updateMacroMenu()

        self.executeMenu = self.menubar.addMenu(self.env.translate("mainWindow.menu.execute"))

        self.executeCommandAction = QAction(self.env.translate("mainWindow.menu.execute.executeCommand"), self)
        self.executeCommandAction.triggered.connect(lambda: self.env.executeCommandWindow.openWindow(self.getTextEditWidget()))
        self.executeCommandAction.setData(["executeCommand"])
        self.env.pluginAPI.addAction(self.executeCommandAction)

        self.editCommandsAction = QAction(self.env.translate("mainWindow.menu.execute.editCommands"), self)
        self.editCommandsAction.triggered.connect(lambda: self.env.editCommandsWindow.openWindow())
        self.editCommandsAction.setData(["editCommands"])
        self.env.pluginAPI.addAction(self.editCommandsAction)

        self.updateExecuteMenu()

        self.aboutMenu = self.menubar.addMenu("&?")

        searchAction = QAction(self.env.translate("mainWindow.menu.about.searchAction"), self)
        searchAction.triggered.connect(lambda: self.env.actionSearchWindow.openWindow())
        searchAction.setData(["searchAction"])
        self.aboutMenu.addAction(searchAction)
        self.env.pluginAPI.addAction(searchAction)

        self.aboutMenu.addSeparator()

        openDataFolder = QAction(self.env.translate("mainWindow.menu.about.openDataDir"),self)
        openDataFolder.triggered.connect(lambda: openFileDefault(self.env.dataDir))
        openDataFolder.setData(["openDataFolder"])
        self.aboutMenu.addAction(openDataFolder)
        self.env.pluginAPI.addAction(openDataFolder)

        openProgramFolder = QAction(self.env.translate("mainWindow.menu.about.openProgramDir"),self)
        openProgramFolder.triggered.connect(lambda: openFileDefault(self.env.programDir))
        openProgramFolder.setData(["openProgramFolder"])
        self.aboutMenu.addAction(openProgramFolder)
        self.env.pluginAPI.addAction(openProgramFolder)

        if self.env.enableUpdater:
            searchForUpdatesAction = QAction(self.env.translate("mainWindow.menu.about.searchForUpdates"),self)
            searchForUpdatesAction.triggered.connect(lambda: searchForUpdates(self.env,False))
            searchForUpdatesAction.setData(["searchForUpdates"])
            self.aboutMenu.addAction(searchForUpdatesAction)
            self.env.pluginAPI.addAction(searchForUpdatesAction)

        showDayTip = QAction(self.env.translate("mainWindow.menu.about.dayTip"),self)
        showDayTip.triggered.connect(lambda: self.env.dayTipWindow.openWindow())
        showDayTip.setData(["showDayTip"])
        self.aboutMenu.addAction(showDayTip)
        self.env.pluginAPI.addAction(showDayTip)

        reportBugAction = QAction(self.env.translate("mainWindow.menu.about.reportBug"),self)
        reportBugAction.triggered.connect(lambda: webbrowser.open("https://gitlab.com/JakobDev/jdTextEdit/issues/new"))
        reportBugAction.setData(["reportBug"])
        self.aboutMenu.addAction(reportBugAction)
        self.env.pluginAPI.addAction(reportBugAction)

        viewDocumentationAction = QAction(self.env.translate("mainWindow.menu.about.viewDocumentation"),self)
        viewDocumentationAction.triggered.connect(lambda: webbrowser.open("https://jdtextedit.readthedocs.io"))
        viewDocumentationAction.setData(["viewDocumentation"])
        self.aboutMenu.addAction(viewDocumentationAction)
        self.env.pluginAPI.addAction(viewDocumentationAction)

        self.aboutMenu.addSeparator()

        debugInfoAction = QAction(QCoreApplication.translate("MainWindow", "Debug information"), self)
        debugInfoAction.triggered.connect(lambda : self.env.debugInfoWindow.openWindow())
        debugInfoAction.setData(["debugInfo"])
        self.aboutMenu.addAction(debugInfoAction)
        self.env.pluginAPI.addAction(debugInfoAction)

        deleteAllDataAction = QAction(QCoreApplication.translate("MainWindow", "Delete all data"), self)
        deleteAllDataAction.triggered.connect(self.deleteAllData)
        deleteAllDataAction.setData(["deleteAllData"])
        self.aboutMenu.addAction(deleteAllDataAction)
        self.env.pluginAPI.addAction(deleteAllDataAction)

        self.aboutMenu.addSeparator()

        about = QAction(self.env.translate("mainWindow.menu.about.about"),self)
        about.triggered.connect(lambda: self.env.aboutWindow.show())
        about.setData(["about"])
        self.aboutMenu.addAction(about)
        self.env.pluginAPI.addAction(about)

        aboutQt = QAction(self.env.translate("mainWindow.menu.about.aboutQt"),self)
        aboutQt.triggered.connect(QApplication.instance().aboutQt)
        aboutQt.setData(["aboutQt"])
        self.aboutMenu.addAction(aboutQt)
        self.env.pluginAPI.addAction(aboutQt)

        self.updateRecentFilesMenu()
        #self.getMenuActions(self.menubar)
        separator = QAction(self.env.translate("mainWindow.separator"))
        separator.setData(["separator"])
        self.env.menuActions["separator"] = separator

    def updateToolbar(self, settings: Settings):
        self.toolbar.clear()
        for i in settings.toolBar:
            if i == "separator":
                self.toolbar.addSeparator()
            else:
                if i in self.env.menuActions:
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
            self.getTextEditWidget().setLanguage(action.data())

    def languagePlainTextClicked(self):
        editWidget = self.getTextEditWidget()
        editWidget.removeLanguage()

    def updateTemplateMenu(self):
        self.templateMenu.clear()

        if len(self.env.templates) == 0:
            empty = QAction(self.env.translate("mainWindow.menu.file.newTemplate.empty"),self)
            empty.setEnabled(False)
            self.templateMenu.addAction(empty)
        else:
            for i in self.env.templates:
                templateAction = QAction(i[0],self)
                templateAction.setData([False,i[1]])
                templateAction.triggered.connect(self.openTemplate)
                self.templateMenu.addAction(templateAction)

        self.templateMenu.addSeparator()
        addMenu = self.templateMenu.addMenu(self.env.translate("mainWindow.menu.file.newTemplate.add"))

        addCurrentDocumentAction = QAction(self.env.translate("mainWindow.menu.file.newTemplate.add.document"),self)
        addCurrentDocumentAction.triggered.connect(self.addCurrentDocumentTemplate)
        addMenu.addAction(addCurrentDocumentAction)

        addFileAction = QAction(self.env.translate("mainWindow.menu.file.newTemplate.add.file"),self)
        addFileAction.triggered.connect(self.addFileTemplate)
        addMenu.addAction(addFileAction)

    def openTemplate(self):
        action = self.sender()
        if action:
            self.openFile(action.data()[1],template=True)

    def addCurrentDocumentTemplate(self):
        """
        This function is called when the user clicks on Templates>Add>Save Document as Template
        """
        name, ok = QInputDialog.getText(self,self.env.translate("mainWindow.menu.file.newTemplate.add.dialog.title"),self.env.translate("mainWindow.menu.file.newTemplate.add.dialog.text"))
        if not ok or name == "":
            return
        if not isFilenameValid(name):
            showMessageBox(self.env.translate("invalidFilename.title"),self.env.translate("invalidFilename.text"))
            return
        path = os.path.join(self.env.dataDir,"templates",name)
        self.saveFile(self.getTextEditWidget(),path=path,template=True)
        self.env.templates.append([name,path])
        self.updateTemplateMenu()

    def addFileTemplate(self):
        """
        This function is called when the user clicks on Templates>Add>Add file as template
        """
        original_path = QFileDialog.getOpenFileName(self)
        if not original_path[0]:
            return
        name, ok = QInputDialog.getText(self,self.env.translate("mainWindow.menu.file.newTemplate.add.dialog.title"),self.env.translate("mainWindow.menu.file.newTemplate.add.dialog.text"))
        if not ok or name == "":
            return
        if not isFilenameValid(name):
            showMessageBox(self.env.translate("invalidFilename.title"),self.env.translate("invalidFilename.text"))
            return
        template_path = os.path.join(self.env.dataDir,"templates",name)
        shutil.copyfile(original_path[0],template_path)
        self.env.templates.append([name,template_path])
        self.updateTemplateMenu()

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
        """
        This function creates the language menu
        """
        self.env.languageActionList = []
        self.env.fileNameFilters = self.env.translate("mainWindow.fileNameFilter.allFiles") + " (*);;"
        self.languageMenu.clear()
        alphabet = {}
        for i in self.env.languageList:
            startLetter = i.getName()[0]
            if not startLetter in alphabet:
                alphabet[startLetter] = []
            alphabet[startLetter].append(i)
        for c in ascii_uppercase:
            if c in alphabet:
                letterMenu = QMenu(c,self)
                for i in alphabet[c]:
                    languageAction = QAction(i.getName(),self)
                    languageAction.setData(i)
                    languageAction.setCheckable(True)
                    languageAction.triggered.connect(self.languageActionClicked)
                    icon = i.getIcon()
                    if icon:
                        languageAction.setIcon(icon)
                    letterMenu.addAction(languageAction)
                    self.env.languageActionList.append(languageAction)
                    self.env.fileNameFilters = self.env.fileNameFilters + i.getName()
                    extensions = i.getExtensions()
                    if len(extensions) != 0:
                        self.env.fileNameFilters = self.env.fileNameFilters + " ("
                        for e in extensions:
                            self.env.fileNameFilters = self.env.fileNameFilters + "*" + e + " "
                        self.env.fileNameFilters = self.env.fileNameFilters[:-1] + ")"
                    self.env.fileNameFilters = self.env.fileNameFilters + ";;"
                self.languageMenu.addMenu(letterMenu)
        self.languageMenu.addSeparator()
        noneAction = QAction(self.env.translate("mainWindow.menu.language.plainText"),self)
        noneAction.triggered.connect(self.languagePlainTextClicked)
        noneAction.setCheckable(True)
        self.env.languagePlainTextAction = noneAction
        self.languageMenu.addAction(noneAction)
        self.env.fileNameFilters = self.env.fileNameFilters + self.env.translate("mainWindow.menu.language.plainText") + " (*.txt)"
        if hasattr(self, "tabWidget"):
           self.updateSelectedLanguage()

    def updateSelectedLanguage(self):
        if not hasattr(self.env, "languageActionList"):
            return
        editWidget = self.getTextEditWidget()
        for i in self.env.languageActionList:
            if i.data().getName() == editWidget.languageName:
                i.setChecked(True)
            else:
                i.setChecked(False)
        if not editWidget.language:
            self.env.languagePlainTextAction.setChecked(True)
        else:
             self.env.languagePlainTextAction.setChecked(False)

    def updateEncodingMenu(self):
        self.encodingMenu.clear()
        self.env.encodingActions = []
        isoMenu = QMenu("ISO", self)
        utfMenu = QMenu("UTF", self)
        windowsMenu = QMenu("windows", self)
        self.encodingMenu.addMenu(isoMenu)
        self.encodingMenu.addMenu(utfMenu)
        self.encodingMenu.addMenu(windowsMenu)
        for i in getEncodingList():
            encodingAction = QAction(i[0], self)
            encodingAction.triggered.connect(self.changeEncoding)
            encodingAction.setCheckable(True)
            self.env.encodingActions.append(encodingAction)
            if i[0].startswith("ISO"):
                isoMenu.addAction(encodingAction)
            elif i[0].startswith("UTF"):
                utfMenu.addAction(encodingAction)
            elif i[0].startswith("windows"):
                windowsMenu.addAction(encodingAction)
            else:
                self.encodingMenu.addAction(encodingAction)

    def changeEncoding(self):
        action = self.sender()
        if action:
            self.getTextEditWidget().setUsedEncoding(action.text())

    def updateMacroMenu(self):
        self.macroMenu.clear()
        self.macroMenu.addAction(self.recordMacroAction)
        self.macroMenu.addAction(self.stopMacroAction)
        self.macroMenu.addAction(self.playMacroAction)
        self.macroMenu.addAction(self.saveMacroAction)
        self.macroMenu.addAction(self.manageMacrosAction)

        if len(self.env.macroList) != 0 or len(self.env.global_macroList):
            self.macroMenu.addSeparator()

        for count, i in enumerate(self.env.macroList):
            singleMacroAction = QAction(i["name"],self)
            singleMacroAction.triggered.connect(self.playMenuMacro)
            singleMacroAction.setShortcut(i["shortcut"])
            singleMacroAction.setData([None,i["macro"]])
            self.macroMenu.addAction(singleMacroAction)

        for count, i in enumerate(self.env.global_macroList):
            singleMacroAction = QAction(i["name"],self)
            singleMacroAction.triggered.connect(self.playMenuMacro)
            singleMacroAction.setShortcut(i["shortcut"])
            singleMacroAction.setData([None,i["macro"]])
            self.macroMenu.addAction(singleMacroAction)

    def playMenuMacro(self):
        action = self.sender()
        if action:
            macro = QsciMacro(self.getTextEditWidget())
            macro.load(action.data()[1])
            macro.play()

    def updateExecuteMenu(self):
        self.executeMenu.clear()

        self.executeMenu.addAction(self.executeCommandAction)

        if len(self.env.commands) != 0 or len(self.env.global_commands):
            self.executeMenu.addSeparator()

        for i in self.env.commands:
            command = QAction(i[0],self)
            command.setData([False,i[1],i[2]])
            if len(i) == 4:
                command.setShortcut(i[3])
            command.triggered.connect(lambda sender: executeCommand(self.env, self.sender().data()[1], self.getTextEditWidget(), self.sender().data()[2]))
            self.executeMenu.addAction(command)

        for i in self.env.global_commands:
            command = QAction(i[0],self)
            command.setData([False, i[1], i[2]])
            command.triggered.connect(lambda sender: executeCommand(self.env, self.sender().data()[1], self.getTextEditWidget(), self.sender().data()[2]))
            self.executeMenu.addAction(command)

        self.executeMenu.addSeparator()

        self.executeMenu.addAction(self.editCommandsAction)


    def openFile(self, path: str, template=None, reload=None):
        #Check if the file is already open
        if not template:
            for tabWidget in self.splitViewWidget.getAllTabWidgets():
                for i in range(tabWidget.count()):
                    if tabWidget.widget(i).getCodeEditWidget().getFilePath() == path:
                        tabWidget.setCurrentIndex(i)
                        tabWidget.setActive()
                        if not reload:
                            return
        #Check if the file exists
        if not os.path.isfile(path):
            return
        #Open the file and show error, if it fails
        try:
            filehandle = open(path,"rb")
        except PermissionError:
            showMessageBox(self.env.translate("noReadPermission.title"),self.env.translate("noReadPermission.text") % path)
            return
        except Exception as e:
            print(e)
            showMessageBox(self.env.translate("unknownError.title"),self.env.translate("unknownError.text"))
            return
        fileBytes = filehandle.read()
        if len(fileBytes) >= self.env.settings.bigFileSize and self.env.settings.enableBigFileLimit:
            isBigFile = True
        else:
            isBigFile = False
        if self.env.settings.detectEncoding and not(isBigFile and self.env.settings.bigFileDisableEncodingDetect):
            encoding = self.env.encodingDetectFunctions[self.env.settings.encodingDetectLib](fileBytes)["encoding"]
            if not encoding:
                encoding = "UTF-8"
            elif encoding == "ascii":
                encoding = "UTF-8"
            for i in getEncodingList():
                if encoding in i:
                    encoding = i[0]
        else:
            encoding = self.env.settings.defaultEncoding
        fileContent = fileBytes.decode(encoding, errors="replace")
        filehandle.close()
        tabWidget = self.getTabWidget()
        if (not self.getTextEditWidget().isNew) and (not reload):
            tabWidget.createTab(self.env.translate("mainWindow.newTabTitle"),focus=True)
        containerWidget = tabWidget.currentWidget()
        editWidget = containerWidget.getCodeEditWidget()
        if isBigFile and self.env.settings.bigFileDisableHighlight:
            editWidget.removeLanguage()
        editWidget.bigFile = isBigFile
        editWidget.setText(fileContent)
        editWidget.setModified(False)
        tabWidget.tabsChanged.emit()
        if not template:
            editWidget.setFilePath(path)
            tabWidget.setTabText(tabWidget.currentIndex(),os.path.basename(path))
        self.updateWindowTitle()
        if self.env.settings.detectEol:
            lines = fileContent.splitlines(True)
            if len(lines) != 0:
                firstLine = lines[0]
                if firstLine.endswith("\r\n"):
                    editWidget.setEolMode(QsciScintilla.EolMode.EolWindows)
                elif firstLine.endswith("\n"):
                    editWidget.setEolMode(QsciScintilla.EolMode.EolUnix)
                elif firstLine.endswith("\r"):
                    editWidget.setEolMode(QsciScintilla.EolMode.EolMac)
        editWidget.updateEolMenu()
        editWidget.setUsedEncoding(encoding)
        if not template:
            count = 0
            for i in self.env.recentFiles:
                if i == path:
                    del self.env.recentFiles[count]
                count += 1
            self.env.recentFiles.insert(0,path)
            self.env.recentFiles = self.env.recentFiles[:self.env.settings.maxRecentFiles]
            self.updateRecentFilesMenu()
        if self.env.settings.detectLanguage and not(isBigFile and self.env.settings.bigFileDisableHighlight):
            languageFound = False
            for i in self.env.languageList:
                for e in i.getExtensions():
                    if path.endswith(e):
                        editWidget.setLanguage(i)
                        languageFound = True
                        break
                if languageFound:
                    break
                for e in i.getStarttext():
                    if fileContent.startswith(e):
                        editWidget.setLanguage(i)
                        languageFound = True
                        break
                if languageFound:
                    break
        containerWidget.clearBanner()
        if self.env.settings.useEditorConfig and not template:
            editWidget.loadEditorConfig()
        if editWidget.settings.defaultEncoding != encoding and self.env.settings.showEncodingBanner:
            containerWidget.showBanner(WrongEncodingBanner(self.env,containerWidget))
        if self.env.settings.showEolBanner:
            if editWidget.eolMode() == QsciScintilla.EolMode.EolWindows and editWidget.settings.defaultEolMode != 0:
                containerWidget.showBanner(WrongEolBanner(self.env,containerWidget))
            elif editWidget.eolMode() == QsciScintilla.EolMode.EolUnix and editWidget.settings.defaultEolMode != 1:
                containerWidget.showBanner(WrongEolBanner(self.env,containerWidget))
            elif editWidget.eolMode() == QsciScintilla.EolMode.EolMac and editWidget.settings.defaultEolMode != 2:
                containerWidget.showBanner(WrongEolBanner(self.env,containerWidget))
        if isBigFile and self.env.settings.bigFileShowBanner:
            containerWidget.showBanner(BigFileBanner(self.env,containerWidget))
        self.env.editorSignals.openFile.emit(editWidget)
        tabWidget.setActive()

    def saveFile(self, editWidget: CodeEdit, path: str = None,template: bool = False):
        containerWidget = editWidget.container
        if not path:
            path = editWidget.getFilePath()
        if not template:
            containerWidget.fileWatcher.removePath(path)
            if os.path.isfile(path) and self.env.settings.saveBackupEnabled:
                shutil.copyfile(path,path + self.env.settings.saveBackupExtension)
        text = editWidget.text()
        eolChar = editWidget.getEolChar()
        if editWidget.settings.eolFileEnd:
            if not text.endswith(eolChar):
                text = text + eolChar
        if editWidget.settings.stripSpacesSave:
            new_text = ""
            for i in text.splitlines():
                new_text = new_text + i.rstrip() + eolChar
            if not text.endswith(eolChar):
                new_text = new_text[:-1]
            text = new_text
        text = text.encode(editWidget.getUsedEncoding(),errors="replace")
        try:
            filehandle = open(path, "wb")
        except PermissionError:
            showMessageBox(self.env.translate("noWritePermission.title"),self.env.translate("noWritePermission.text") % editWidget.getFilePath())
            return
        except Exception as e:
            print(e)
            showMessageBox(self.env.translate("unknownError.title"),self.env.translate("unknownError.text"))
            return
        filehandle.write(text)
        filehandle.close()
        if template:
            return
        containerWidget.fileWatcher.addPath(path)
        editWidget.setModified(False)
        self.updateWindowTitle()
        if len(text) >= self.env.settings.get("bigFileSize") and self.env.settings.get("enableBigFileLimit"):
            isBigFile = True
        else:
            isBigFile = False
        if self.env.settings.get("detectLanguage") and not(isBigFile and self.env.settings.get("bigFileDisableHighlight")):
            languageFound = False
            for i in self.env.languageList:
                for e in i.getExtensions():
                    if path.endswith(e):
                        editWidget.setLanguage(i)
                        languageFound = True
                        break
                if languageFound:
                    break
                for e in i.getStarttext():
                    if text.startswith(e.encode("utf-8")):
                        editWidget.setLanguage(i)
                        languageFound = True
                        break
                if languageFound:
                    break

    def newMenuBarClicked(self):
        self.getTabWidget().createTab(self.env.translate("mainWindow.newTabTitle"), focus=True)

    def openMenuBarClicked(self):
        pathTypeSetting = self.env.settings.get("openFilePathType")
        if pathTypeSetting == 0:
            #Use path of current file
            startPath = os.path.dirname(self.getTextEditWidget().getFilePath())
        elif pathTypeSetting == 1:
            #Use latest Path
            startPath = self.env.lastOpenPath
        elif pathTypeSetting == 2:
            #Use custom path
            startPath = self.env.settings.get("openFileCustomPath")

        path = QFileDialog.getOpenFileName(self,self.env.translate("mainWindow.openFileDialog.title"), startPath, self.env.fileNameFilters)
        if path[0]:
            self.openFile(path[0])
            self.env.lastOpenPath = path[0]

    def openDirectoryMenuBarClicked(self):
        pathTypeSetting = self.env.settings.get("openFilePathType")
        if pathTypeSetting == 0:
            #Use path of current file
            startPath =os.path.dirname(self.getTextEditWidget().getFilePath())
        elif pathTypeSetting == 1:
            #Use latest Path
            startPath = self.env.lastOpenPath
        elif pathTypeSetting == 2:
            #Use custom path
            startPath = self.env.settings.get("openFileCustomPath")

        path = QFileDialog.getExistingDirectory(self, self.env.translate("mainWindow.openDirectoryDialog.title"),startPath)
        if path:
            self.env.lastOpenPath = path
            fileList = os.listdir(path)
            for i in fileList:
                filePath = os.path.join(path, i)
                if os.path.isfile(filePath):
                    self.openFile(filePath)

    def saveMenuBarClicked(self, editWidget: CodeEdit):
        if editWidget.getFilePath() == "":
            self.saveAsMenuBarClicked(editWidget)
        else:
            self.saveFile(editWidget)

    def deleteMenuBarClicked(self):
        lastText = self.env.clipboard.text()
        self.getTextEditWidget().cut()
        self.env.clipboard.setText(lastText)

    def saveAsMenuBarClicked(self,editWidget: CodeEdit):
        pathTypeSetting = self.env.settings.get("saveFilePathType")
        if pathTypeSetting == 0:
            # Use path of current file
            startPath =os.path.dirname(editWidget.getFilePath())
        elif pathTypeSetting == 1:
            # Use latest Path
            startPath = self.env.lastSavePath
        elif pathTypeSetting == 2:
            # Use custom path
            startPath = self.env.settings.get("saveFileCustomPath")
        path = QFileDialog.getSaveFileName(self,self.env.translate("mainWindow.saveAsDialog.title"), startPath, self.env.fileNameFilters)

        if path[0]:
            self.getTextEditWidget().setFilePath(path[0])
            self.saveFile(editWidget)
            tabWidget = editWidget.container.getTabWidget()
            tabWidget.setTabText(editWidget.tabid,os.path.basename(path[0]))
            tabWidget.tabsChanged.emit()
            self.updateWindowTitle()
            self.env.lastSavePath = path

    def saveAllMenuBarClicked(self):
        for tabWidget in self.splitViewWidget.getAllTabWidgets():
            for i in range(tabWidget.count()):
                self.saveMenuBarClicked(tabWidget.widget(i))

    def closeAllTabs(self):
        for tabWidget in self.splitViewWidget.getAllTabWidgets():
            for i in range(tabWidget.count()-1,-1,-1):
                tabWidget.tabCloseClicked(i,notCloseProgram=True)
        self.splitViewWidget.initTabWidget()
        self.getTabWidget().createTab(self.env.translate("mainWindow.newTabTitle"),focus=True)

    def printMenuBarClicked(self):
        """
        This function is called when the user clicks File>Print
        :return:
        """
        printer = QsciPrinter()
        dialog = QPrintDialog(printer)
        dialog.setWindowTitle(self.env.translate("mainWindow.printDialog.title"))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            editWidget = self.getTextEditWidget()
            printer.printRange(editWidget)

    def getCurrentLines(self) -> List[str]:
        """
        Retruns the current selected lines. Returns all lines if nothing is selected.
        :return: lines
        """
        editWidget = self.getTextEditWidget()
        if editWidget.hasSelectedText():
            selection = editWidget.getSelection()
            startLine = selection[0]
            endLine = selection[2]
        else:
            startLine = 0
            endLine = editWidget.lines()-1
        lines = []
        for i in range(startLine, endLine + 1):
            lines.append(editWidget.text(i))
        eolChar = editWidget.getEolChar()
        if not lines[-1].endswith(eolChar):
            lines[-1] += eolChar
        return lines

    def replaceCurrentLines(self,lines: List[str]):
        """
        Replaces the current lines with the given lines
        """
        editWidget = self.getTextEditWidget()
        if editWidget.hasSelectedText():
            selection = editWidget.getSelection()
            startLine = selection[0]
            endLine = selection[2]
        else:
            startLine = 0
            endLine = editWidget.lines()
        editWidget.setSelection(startLine, 0, endLine, editWidget.lineLength(endLine))
        editWidget.removeSelectedText()
        editWidget.setCursorPosition(startLine, editWidget.lineLength(startLine))
        for i in lines:
            editWidget.insertText(i)

    def duplicateCurrentLine(self):
        """
        This function is called when the user clicks Edit>Line Operations>Duplicate Current Line
        """
        editWidget = self.getTextEditWidget()
        line = editWidget.text(editWidget.cursorPosLine)
        editWidget.setCursorPosition(editWidget.cursorPosLine,len(line))
        editWidget.insertText(line)

    def removeCurrentLine(self):
        """
        This function is called when the user clicks Edit>Line Operations>Delete Current Line
        """
        editWidget = self.getTextEditWidget()
        length = editWidget.lineLength(editWidget.cursorPosLine)
        editWidget.setSelection(editWidget.cursorPosLine,0,editWidget.cursorPosLine,length)
        editWidget.removeSelectedText()

    def sortLinesAlphabetical(self):
        lines = self.getCurrentLines()
        print(lines)
        lines.sort()
        self.replaceCurrentLines(lines)

    def shuffleLines(self):
        """
        This function is called when the user clicks Edit>Line Operations>Shuffle Lines
        """
        editWidget = self.getTextEditWidget()
        if editWidget.hasSelectedText():
            selection = editWidget.getSelection()
            startLine = selection[0]
            endLine = selection[2]
        else:
            startLine = 0
            endLine = editWidget.lines()
        lines = []
        for i in range(startLine,endLine+1):
            lines.append(editWidget.text(i))
        random.shuffle(lines)
        editWidget.setSelection(startLine, 0, endLine, editWidget.lineLength(endLine))
        editWidget.removeSelectedText()
        editWidget.setCursorPosition(startLine, editWidget.lineLength(startLine))
        for i in lines:
            editWidget.insertText(i)

    def setCustomZoom(self):
        """
        This function is called when the user clicks View>Zoom>Custom
        """
        editWidget = self.getTextEditWidget()
        currentZoom = (editWidget.getZoom()+10)*10
        scale,ok = QInputDialog.getInt(self,self.env.translate("mainWindow.menu.view.zoom.zoomCustom.titel"), self.env.translate("mainWindow.menu.view.zoom.zoomCustom.text"),currentZoom,0,300,10)
        if not ok:
            return
        scale -= 100
        editWidget.zoomTo(int(scale / 10))

    def fullscreenMenuBarClicked(self):
        """
        This function is called when the user clicks View>Fullscreen
        """
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
        self.fullscreenAction.setChecked(self.isFullScreen())

    def searchAndReplaceMenuBarClicked(self):
        self.env.searchReplaceWindow.display(self.getTextEditWidget())

    def pickColorClicked(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.getTextEditWidget().insertText(col.name())

    def stripSpaces(self):
        editWidget = self.getTextEditWidget()
        eolChar = editWidget.getEolChar()
        if editWidget.selectedText() == "":
            text = editWidget.text()
        else:
            text = editWidget.selectedText()
        new_text = ""
        for i in text.splitlines():
            new_text = new_text + i.rstrip() + eolChar
        if not text.endswith(eolChar):
            new_text = new_text[:-1]
        line = editWidget.cursorPosLine
        if editWidget.selectedText() == "":
            editWidget.setText(new_text)
        else:
            editWidget.replaceSelectedText(new_text)
        editWidget.setCursorPosition(line,0)

    def replaceTabSpaces(self):
        editWidget = self.getTextEditWidget()
        spaceString = ""
        for i in range(self.env.settings.editTabWidth):
            spaceString = spaceString + " "
        line = editWidget.cursorPosLine
        if editWidget.selectedText() == "":
            text = editWidget.text()
            text = text.replace("\t",spaceString)
            editWidget.setText(text)
        else:
            text = editWidget.selectedText()
            text = text.replace("\t",spaceString)
            editWidget.replaceSelectedText(text)
        editWidget.setCursorPosition(line,0)

    def replaceSpacesTab(self):
        editWidget = self.getTextEditWidget()
        spaceString = ""
        for i in range(self.env.settings.editTabWidth):
            spaceString = spaceString + " "
        line = editWidget.cursorPosLine
        if editWidget.selectedText() == "":
            text = editWidget.text()
            text = text.replace(spaceString,"\t")
            editWidget.setText(text)
        else:
            text = editWidget.selectedText()
            text = text.replace(spaceString,"\t")
            editWidget.replaceSelectedText(text)
        editWidget.setCursorPosition(line,0)

    def toggleSidebarClicked(self):
        if self.env.sidepane.enabled:
            self.env.sidepane.enabled = False
            self.env.sidepane.hide()
        else:
            self.env.sidepane.enabled = True
            self.env.sidepane.show()
        self.toggleSidebarAction.setChecked(self.env.sidepane.enabled)

    def addRemoveBookmark(self):
        editWidget = self.getTextEditWidget()
        line = editWidget.cursorPosLine
        editWidget.addRemoveBookmark(line)

    def nextBookmark(self):
        editWidget = self.getTextEditWidget()
        if len(editWidget.bookmarkList) == 0:
            return
        line = editWidget.cursorPosLine
        for i in editWidget.bookmarkList:
            if i > line:
                editWidget.setCursorPosition(i,0)
                return
        editWidget.setCursorPosition(editWidget.bookmarkList[0],0)

    def previousBookmark(self):
        editWidget = self.getTextEditWidget()
        if len(editWidget.bookmarkList) == 0:
            return
        line = editWidget.cursorPosLine
        oldBookmark = editWidget.bookmarkList[-1]
        for i in editWidget.bookmarkList:
            if i >= line:
                editWidget.setCursorPosition(oldBookmark,0)
                return
            oldBookmark = i

    def clearBookmarks(self):
        editWidget = self.getTextEditWidget()
        for i in editWidget.bookmarkList:
            editWidget.markerDelete(i,0)
        editWidget.bookmarkList = []

    def startMacroRecording(self):
        self.currentMacro = QsciMacro(self.getTextEditWidget())
        self.currentMacro.startRecording()
        self.recordMacroAction.setEnabled(False)
        self.stopMacroAction.setEnabled(True)

    def stopMacroRecording(self):
        self.currentMacro.endRecording()
        self.recordMacroAction.setEnabled(True)
        self.stopMacroAction.setEnabled(False)
        self.playMacroAction.setEnabled(True)
        self.saveMacroAction.setEnabled(True)

    def playMacro(self):
        self.currentMacro.play()

    def saveMacro(self):
        name, ok = QInputDialog.getText(self,self.env.translate("mainWindow.messageBox.saveMacro.title"),self.env.translate("mainWindow.messageBox.saveMacro.text"))
        if not ok or name == '':
            return
        self.env.macroList.append({"name":name,"macro":self.currentMacro.save(),"shortcut":""})
        self.updateMacroMenu()
        with open(os.path.join(self.env.dataDir,"macros.json"), 'w', encoding='utf-8') as f:
            json.dump(self.env.macroList, f, ensure_ascii=False, indent=4)

    def deleteAllData(self):
        if QMessageBox.question(self, QCoreApplication.translate("MainWindow", "Delete all data"), QCoreApplication.translate("MainWindow", "This will delete all data of jdTextEdit. After that, jdTextEdit will behave like the first run. jdTexEdit will exit after doing that. Are you sure?")) != QMessageBox.StandardButton.Yes:
            return

        try:
            shutil.rmtree(self.env.dataDir)
        except Exception:
            print(traceback.format_exc(), end="", file=sys.stderr)
            showMessageBox(self.env.translate("unknownError.title"), self.env.translate("unknownError.text"))
            return

        sys.exit(0)

    def autoSaveTimeout(self):
        if self.autoSaveTimer.timeout == 0 or not self.env.settings.enableAutoSave:
            return
        for tabWidget in self.splitViewWidget.getAllTabWidgets():
            for i in range(tabWidget.count()):
                editWidget = tabWidget.widget(i).getCodeEditWidget()
                if editWidget.getFilePath() != "":
                    self.saveFile(editWidget)

    def updateSettings(self, settings: Settings):
        self.env.recentFiles = self.env.recentFiles[:self.env.settings.maxRecentFiles]
        self.updateRecentFilesMenu()
        self.updateToolbar(settings)
        toolButtonStyle = (Qt.ToolButtonStyle.ToolButtonIconOnly,Qt.ToolButtonStyle.ToolButtonTextOnly,Qt.ToolButtonStyle.ToolButtonTextBesideIcon,Qt.ToolButtonStyle.ToolButtonTextUnderIcon,Qt.ToolButtonStyle.ToolButtonFollowStyle)
        self.setToolButtonStyle(toolButtonStyle[settings.get("toolbarIconStyle")])
        if settings.showToolbar:
            self.toolbar.show()
        else:
            self.toolbar.close()
        toolbarPositionList = [Qt.ToolBarArea.TopToolBarArea,Qt.ToolBarArea.BottomToolBarArea,Qt.ToolBarArea.LeftToolBarArea,Qt.ToolBarArea.RightToolBarArea]
        self.addToolBar(toolbarPositionList[settings.toolbarPosition],self.toolbar)
        if settings.applicationStyle == "default":
            QApplication.setStyle(QStyleFactory.create(self.env.defaultStyle))
        else:
            QApplication.setStyle(QStyleFactory.create(settings.applicationStyle))
        for key, value in self.env.menuActions.items():
            if key in settings.shortcut:
                value.setShortcut(settings.shortcut[key])
            else:
                value.setShortcut("")
        if self.autoSaveTimer.interval()/1000 != settings.autoSaveInterval:
            self.autoSaveTimer.setInterval(settings.autoSaveInterval * 1000)
        if settings.enableAutoSave:
            self.autoSaveTimer.start()
        else:
            self.autoSaveTimer.stop()
        for i in self.splitViewWidget.getAllTabWidgets():
            i.updateSettings(settings)
        self.updateWindowTitle()

    def updateWindowTitle(self):
        if self.env.settings.windowFileTitle:
            tabWidget = self.getTabWidget()
            self.setWindowTitle(tabWidget.tabText(tabWidget.currentIndex()) + " - jdTextEdit")
        else:
            self.setWindowTitle("jdTextEdit")

    def saveSession(self):
        if not os.path.isdir(os.path.join(self.env.dataDir, "session_data")):
            os.mkdir(os.path.join(self.env.dataDir, "session_data"))
        data = self.splitViewWidget.getSessionData()
        if self.currentMacro:
            data["currentMacro"] = self.currentMacro.save()
        with open(os.path.join(self.env.dataDir, "session.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def restoreSession(self):
        with open(os.path.join(self.env.dataDir,"session.json"),"r",encoding="utf-8") as f:
            data = json.load(f)
        self.splitViewWidget.restoreSession(data)
        self.updateSelectedLanguage()
        if "currentMacro" in data:
            self.currentMacro = QsciMacro(self.getTextEditWidget())
            self.currentMacro.load(data["currentMacro"])
            self.playMacroAction.setEnabled(True)
            self.saveMacroAction.setEnabled(True)
        os.remove(os.path.join(self.env.dataDir, "session.json"))
        shutil.rmtree(os.path.join(self.env.dataDir, "session_data"))

    def saveDataClose(self):
        self.env.settings.showSidepane = self.env.sidepane.enabled
        self.env.settings.sidepaneWidget = self.env.sidepane.content.getSelectedWidget()
        self.env.settings.save(os.path.join(self.env.dataDir, "settings.json"))
        saveProjects(self.env.projects, os.path.join(self.env.dataDir, "projects.json"))
        if self.env.settings.saveWindowState:
            windowState = {}
            saveWindowState(self,windowState, "MainWindow")
            saveWindowState(self.env.settingsWindow, windowState, "SettingsWindow")
            saveWindowState(self.env.dayTipWindow, windowState, "DayTipWindow")
            saveWindowState(self.env.editCommandsWindow, windowState, "EditCommandsWindow")
            saveWindowState(self.env.dateTimeWindow, windowState, "DateTimeWindow")
            saveWindowState(self.env.manageMacrosWindow, windowState, "ManageMacrosWindow")
            saveWindowState(self.env.actionSearchWindow, windowState, "ActionSearchWindow")
            saveWindowState(self.env.debugInfoWindow, windowState, "DebugInfoWindow")
            with open(os.path.join(self.env.dataDir, "windowstate.json"), 'w', encoding='utf-8') as f:
                json.dump(windowState, f, ensure_ascii=False, indent=4)
        else:
            try:
                os.remove(os.path.join(self.env.dataDir,"windowstate.json"))
            except:
                pass
        with open(os.path.join(self.env.dataDir, "lastversion.txt"), "w", encoding="utf-8") as f:
            f.write(self.env.version)

    def closeEvent(self, event):
        self.saveDataClose()
        if self.env.settings.saveSession:
            try:
                self.saveSession()
            except Exception as e:
                print(traceback.format_exc(), end="")
            sys.exit(0)
        else:
            for tabWidget in self.splitViewWidget.getAllTabWidgets():
                for i in range(tabWidget.count()-1,-1,-1):
                    try:
                        tabWidget.tabCloseClicked(i,forceExit=True)
                    except Exception as e:
                        print(traceback.format_exc(), end="", file=sys.stderr)
            event.ignore()

    def removeTempOpenFile(self):
        try:
            os.remove(getTempOpenFilePath())
        except:
            pass

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ingore()

    def dropEvent(self, event):
        for i in event.mimeData().urls():
            if i.url().startswith("file://"):
                self.openFile(i.url()[7:])

    def contextMenuEvent(self, event):
        pass
