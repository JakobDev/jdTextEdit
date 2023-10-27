from jdTextEdit.Functions import executeCommand, getThemeIcon, openFileDefault, showMessageBox, saveWindowState, restoreWindowState, getTempOpenFilePath, isFilenameValid, saveProjects, clearStatusBar, formatDateTime
from PyQt6.QtWidgets import QMainWindow, QMenu, QApplication, QFileDialog, QStyleFactory, QDialog, QColorDialog, QInputDialog, QMessageBox
from PyQt6.Qsci import QsciScintilla, QsciScintillaBase, QsciMacro, QsciPrinter
from PyQt6.QtGui import QIcon, QAction, QCloseEvent, QDropEvent
from PyQt6.QtPrintSupport import QPrintDialog
from PyQt6.QtCore import Qt, QFileSystemWatcher, QTimer, QCoreApplication
from jdTextEdit.gui.EditTabWidget import EditTabWidget
from jdTextEdit.gui.SplitViewWidget import SplitViewWidget
from jdTextEdit.EncodingList import getEncodingList
from jdTextEdit.gui.DockWidget import DockWidget
from jdTextEdit.Updater import searchForUpdates
from jdTextEdit.gui.BannerWidgets.WrongEncodingBanner import WrongEncodingBanner
from jdTextEdit.gui.BannerWidgets.WrongEolBanner import WrongEolBanner
from jdTextEdit.gui.BannerWidgets.BigFileBanner import BigFileBanner
from jdTextEdit.gui.BannerWidgets.SimpleMessageBanner import SimpleMessageBanner
from jdTextEdit.gui.ManageTemplatesWindow import ManageTemplatesWindow
from jdTextEdit.gui.Windows.ExportDataWindow import ExportDataWindow
from jdTextEdit.gui.Windows.LanguageOverwritesWindow import LanguageOverwritesWindow
from jdTextEdit.gui.Windows.ManageThemesWindow.ManageThemeListWindow import ManageThemeListWindow
from jdTextEdit.gui.CodeEdit import CodeEdit
from jdTextEdit.Settings import Settings
from jdTextEdit.Environment import Environment
from jdTextEdit.api.StatusBarWidgetBase import StatusBarWidgetBase
from string import ascii_uppercase
from typing import Optional, Any
import webbrowser
import traceback
import datetime
import zipfile
import random
import shutil
import atexit
import json
import sys
import os


class MainWindow(QMainWindow):
    def __init__(self, env: Environment):
        super().__init__()
        self.env = env
        self.currentMacro: Optional[QsciMacro] = None
        self.setupMenubar()
        self.splitViewWidget = SplitViewWidget(env, self)
        self.toolbar = self.addToolBar("toolbar")
        self.setCentralWidget(self.splitViewWidget)
        self.autoSaveTimer = QTimer()
        #self.autoSaveTimer.setInterval(2147483647)
        self.autoSaveTimer.timeout.connect(self.autoSaveTimeout)
        if "MainWindow" in env.windowState:
            restoreWindowState(self, env.windowState ,"MainWindow")
        else:
            self.setGeometry(0, 0, 800, 600)

    def setup(self):
        #This is called, after all at least
        if os.path.isfile(os.path.join(self.env.dataDir, "session.json")) and not self.env.args["disableSessionRestore"]:
            try:
                self.restoreSession()
            except Exception as e:
                self.env.logger.exception(e)
                showMessageBox("Error","Could not restore session. This might be happen after an Update. If jdTextEdit crashes just restart it.")
                os.remove(os.path.join(self.env.dataDir,"session.json"))
                shutil.rmtree(os.path.join(self.env.dataDir,"session_data"))
                tabWidget = self.splitViewWidget.getCurrentTabWidget()
                if tabWidget.count() == 0:
                    tabWidget.createTab(QCoreApplication.translate("MainWindow", "Untitled"))
        else:
            self.splitViewWidget.initTabWidget()
            self.splitViewWidget.getCurrentTabWidget().createTab(QCoreApplication.translate("MainWindow", "Untitled"))
        self.updateLanguageMenu()

        # Open paths from commandline
        for current_path in self.env.args["path"]:
            self.openFileCommandline(os.path.abspath(current_path))

        #self.getMenuActions(self.menubar)
        self.sidepane = DockWidget(self.env)
        self.sidepane.hide()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sidepane)
        for tabWidget in self.splitViewWidget.getAllTabWidgets():
            for i in range(tabWidget.count()):
                widget = tabWidget.widget(i).getCodeEditWidget()
                widget.modificationStateChange(widget.isModified())
        if self.env.settings.get("showSidepane"):
            self.toggleSidebarClicked()
        self.sidepane.content.setCurrentWidget(self.env.settings.get("sidepaneWidget"))
        self.getTextEditWidget().updateEolMenu()
        self.getTextEditWidget().updateEncodingMenu()
        self.env.settingsWindow.setup()
        self.env.dayTipWindow.setup()
        self.updateSettings(self.env.settings)
        if self.env.settings.get("searchUpdates") and self.env.enableUpdater:
            searchForUpdates(self, self.env, True)
        if self.env.settings.get("useIPC"):
            open(getTempOpenFilePath(), "w").close()
            self.tempFileOpenWatcher = QFileSystemWatcher()
            self.tempFileOpenWatcher.addPath(getTempOpenFilePath())
            self.tempFileOpenWatcher.fileChanged.connect(self.openTempFileSignal)
            atexit.register(self.removeTempOpenFile)
        self.env.mainWindowSignals.windowInit.emit(self)
        self.show()
        #self.getTextEditWidget().ensureCursorVisible()
        if self.env.settings.get("startupDayTip"):
            self.env.dayTipWindow.openWindow()

    def openFileCommandline(self, path: str):
        if os.path.isfile(path):
            self.openFile(path)
        else:
            #Check if the file is already open but do not exists anymore
            found = False
            for tabWidget in self.splitViewWidget.getAllTabWidgets():
                for i in range(tabWidget.count()):
                    if tabWidget.editWidget(i).getFilePath() == path:
                        tabWidget.setCurrentIndex(i)
                        found = True
            if not found:
                if os.path.isdir(path):
                    self.env.logger.error("Can't open directory")
                else:
                    self.getTabWidget().createTab(os.path.basename(path), focus=True)
                    editWidget = self.getTextEditWidget()
                    editWidget.setFilePath(path)
                    editWidget.isNew = False
                    if self.env.settings.get("useEditorConfig"):
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

    def _handleTempFileData(self, data: dict[str, Any]) -> None:
        match data["action"]:
            case "openFile":
                for path in data["path"]:
                    self.openFileCommandline(path)
            case "writeWindowID":
                with open(data["file"], "w", encoding="utf-8") as f:
                    f.write(str(int(self.effectiveWinId())))

    def openTempFileSignal(self, path: str):
        if os.path.getsize(path) == 0:
            return

        data = None
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                self.env.logger.exception(e)

        if data is not None:
            try:
                self._handleTempFileData(data)
            except Exception as e:
                self.env.logger.exception(e)

        open(path, "w").close()
        self.tempFileOpenWatcher.addPath(path)
        QApplication.setActiveWindow(self)
        self.activateWindow()

    def setupMenubar(self) -> None:
        """
        Creates the Menubar with all Actions
        """
        self.menubar = self.menuBar()
        self.recentFilesMenu = QMenu(QCoreApplication.translate("MainWindow", "Open Recent Files"))
        self.recentFilesMenu.setIcon(getThemeIcon(self.env, "document-open-recent"))

        self.filemenu = self.menubar.addMenu(QCoreApplication.translate("MainWindow", "&File"))

        new = QAction(QCoreApplication.translate("MainWindow", "&New"), self)
        new.setIcon(getThemeIcon(self.env,"document-new"))
        new.triggered.connect(self.newMenuBarClicked)
        new.setData(["newFile"])
        self.filemenu.addAction(new)
        self.env.pluginAPI.addAction(new)

        self.templateMenu = QMenu(QCoreApplication.translate("MainWindow", "New (from Template)"), self)
        self.templateMenu.setIcon(getThemeIcon(self.env, "document-new"))
        self.updateTemplateMenu()
        self.filemenu.addMenu(self.templateMenu)

        self.filemenu.addSeparator()

        openmenu = QAction(QCoreApplication.translate("MainWindow", "&Open"), self)
        openmenu.setIcon(getThemeIcon(self.env, "document-open"))
        openmenu.triggered.connect(self.openMenuBarClicked)
        openmenu.setData(["openFile"])
        self.filemenu.addAction(openmenu)
        self.env.pluginAPI.addAction(openmenu)

        openDirectoryMenu = QAction(QCoreApplication.translate("MainWindow", "Open Directory"), self)
        openDirectoryMenu.setIcon(getThemeIcon(self.env, "folder-open"))
        openDirectoryMenu.triggered.connect(self.openDirectoryMenuBarClicked)
        openDirectoryMenu.setData(["directoryOpen"])
        self.filemenu.addAction(openDirectoryMenu)
        self.env.pluginAPI.addAction(openDirectoryMenu)

        self.filemenu.addMenu(self.recentFilesMenu)

        self.filemenu.addSeparator()

        save = QAction(QCoreApplication.translate("MainWindow", "&Save"), self)
        save.setIcon(getThemeIcon(self.env, "document-save"))
        save.triggered.connect(lambda: self.saveMenuBarClicked(self.getTextEditWidget()))
        save.setData(["saveFile"])
        self.filemenu.addAction(save)
        self.env.pluginAPI.addAction(save)

        saveAs = QAction(QCoreApplication.translate("MainWindow", "Save as ..."), self)
        saveAs.setIcon(getThemeIcon(self.env, "document-save-as"))
        saveAs.triggered.connect(lambda: self.saveAsMenuBarClicked(self.getTextEditWidget()))
        saveAs.setData(["saveAsFile"])
        self.filemenu.addAction(saveAs)
        self.env.pluginAPI.addAction(saveAs)

        saveAll = QAction(QCoreApplication.translate("MainWindow", "Save all"), self)
        saveAll.setIcon(getThemeIcon(self.env, "document-save-all"))
        saveAll.triggered.connect(self.saveAllMenuBarClicked)
        saveAll.setData(["saveAll"])
        self.filemenu.addAction(saveAll)
        self.env.pluginAPI.addAction(saveAll)

        self.filemenu.addSeparator()

        closeTab = QAction(QCoreApplication.translate("MainWindow", "Close"), self)
        closeTab.setIcon(QIcon(os.path.join(self.env.programDir, "icons", "document-close.png")))
        closeTab.triggered.connect(lambda: self.getTabWidget().tabCloseClicked(self.getTabWidget().currentIndex()))
        closeTab.setData(["closeTab"])
        self.filemenu.addAction(closeTab)
        self.env.pluginAPI.addAction(closeTab)

        closeAllTabsAction = QAction(QCoreApplication.translate("MainWindow", "Close all tabs"), self)
        closeAllTabsAction.setIcon(QIcon(os.path.join(self.env.programDir, "icons", "document-close-all.png")))
        closeAllTabsAction.triggered.connect(self.closeAllTabs)
        closeAllTabsAction.setData(["closeAllTabs"])
        self.filemenu.addAction(closeAllTabsAction)
        self.env.pluginAPI.addAction(closeAllTabsAction)

        self.filemenu.addSeparator()

        printMenuItem = QAction(QCoreApplication.translate("MainWindow", "&Print"), self)
        printMenuItem.setIcon(getThemeIcon(self.env,"document-print"))
        printMenuItem.triggered.connect(self.printMenuBarClicked)
        printMenuItem.setData(["print"])
        self.filemenu.addAction(printMenuItem)
        self.env.pluginAPI.addAction(printMenuItem)

        exit = QAction(QCoreApplication.translate("MainWindow", "&Exit"), self)
        exit.setIcon(getThemeIcon(self.env,"application-exit"))
        exit.triggered.connect(self.close)
        exit.setData(["exit"])
        self.filemenu.addAction(exit)
        self.env.pluginAPI.addAction(exit)

        self.menubar.addMenu(self.filemenu)
        self.editMenu = self.menubar.addMenu(QCoreApplication.translate("MainWindow", "&Edit"))

        self.undoMenubarItem = QAction(QCoreApplication.translate("MainWindow", "&Undo"), self)
        self.undoMenubarItem.setIcon(getThemeIcon(self.env, "edit-undo"))
        self.undoMenubarItem.triggered.connect(lambda: self.getTextEditWidget().undo())
        self.undoMenubarItem.setData(["undo"])
        self.editMenu.addAction(self.undoMenubarItem)
        self.env.pluginAPI.addAction(self.undoMenubarItem)
        self.undoMenubarItem.setEnabled(False)

        self.redoMenubarItem = QAction(QCoreApplication.translate("MainWindow", "&Redo"), self)
        self.redoMenubarItem.setIcon(getThemeIcon(self.env, "edit-redo"))
        self.redoMenubarItem.triggered.connect(lambda: self.getTextEditWidget().redo())
        self.redoMenubarItem.setData(["redo"])
        self.editMenu.addAction(self.redoMenubarItem)
        self.env.pluginAPI.addAction(self.redoMenubarItem)
        self.redoMenubarItem.setEnabled(False)

        self.editMenu.addSeparator()

        self.cutMenubarItem = QAction(QCoreApplication.translate("MainWindow", "&Cut"), self)
        self.cutMenubarItem.setIcon(getThemeIcon(self.env, "edit-cut"))
        self.cutMenubarItem.triggered.connect(lambda: self.getTextEditWidget().cut())
        self.cutMenubarItem.setData(["cut"])
        self.editMenu.addAction(self.cutMenubarItem)
        self.env.pluginAPI.addAction(self.cutMenubarItem)
        self.cutMenubarItem.setEnabled(False)

        self.copyMenubarItem = QAction(QCoreApplication.translate("MainWindow", "&Copy"), self)
        self.copyMenubarItem.setIcon(getThemeIcon(self.env, "edit-copy"))
        self.copyMenubarItem.triggered.connect(lambda: self.getTextEditWidget().copy())
        self.copyMenubarItem.setData(["copy"])
        self.editMenu.addAction(self.copyMenubarItem)
        self.env.pluginAPI.addAction(self.copyMenubarItem)
        self.copyMenubarItem.setEnabled(False)

        paste = QAction(QCoreApplication.translate("MainWindow", "&Paste"), self)
        paste.setIcon(getThemeIcon(self.env,"edit-paste"))
        paste.triggered.connect(lambda: self.getTextEditWidget().paste())
        paste.setData(["paste"])
        self.editMenu.addAction(paste)
        self.env.pluginAPI.addAction(paste)

        self.deleteMenubarItem = QAction(QCoreApplication.translate("MainWindow", "&Delete"), self)
        self.deleteMenubarItem.setIcon(getThemeIcon(self.env, "edit-delete"))
        self.deleteMenubarItem.triggered.connect(lambda: self.getTextEditWidget().removeSelectedText())
        self.deleteMenubarItem.setData(["delete"])
        self.editMenu.addAction(self.deleteMenubarItem)
        self.env.pluginAPI.addAction(self.deleteMenubarItem)
        self.deleteMenubarItem.setEnabled(False)

        self.editMenu.addSeparator()

        selectAll = QAction(QCoreApplication.translate("MainWindow", "&Select All"), self)
        selectAll.setIcon(getThemeIcon(self.env, "edit-select-all"))
        selectAll.triggered.connect(lambda: self.getTextEditWidget().selectAll())
        selectAll.setData(["selectAll"])
        self.editMenu.addAction(selectAll)
        self.env.pluginAPI.addAction(selectAll)

        self.editMenu.addSeparator()

        self.clipboardCopyMenu = QMenu(QCoreApplication.translate("MainWindow", "Copy to Clipboard"), self)

        copyPath = QAction(QCoreApplication.translate("MainWindow", "Copy Full Path to Clipboard"), self)
        copyPath.triggered.connect(lambda: self.env.clipboard.setText(self.getTextEditWidget().getFilePath()))
        copyPath.setData(["copyPath"])
        self.clipboardCopyMenu.addAction(copyPath)
        self.env.pluginAPI.addAction(copyPath)

        copyDirectory = QAction(QCoreApplication.translate("MainWindow", "Copy Directory to Clipboard"), self)
        copyDirectory.triggered.connect(lambda: self.env.clipboard.setText(os.path.dirname(self.getTextEditWidget().getFilePath())))
        copyDirectory.setData(["copyDirectory"])
        self.clipboardCopyMenu.addAction(copyDirectory)
        self.env.pluginAPI.addAction(copyDirectory)

        copyFilename = QAction(QCoreApplication.translate("MainWindow", "Copy Filename to Clipboard"), self)
        copyFilename.triggered.connect(lambda: self.env.clipboard.setText(os.path.basename(self.getTextEditWidget().getFilePath())))
        copyFilename.setData(["copyFilename"])
        self.clipboardCopyMenu.addAction(copyFilename)
        self.env.pluginAPI.addAction(copyFilename)

        copyUrlAction = QAction(QCoreApplication.translate("MainWindow", "Copy URL to Clipboard"), self)
        copyUrlAction.triggered.connect(lambda: self.env.clipboard.setText("file://" + self.getTextEditWidget().getFilePath()))
        copyUrlAction.setData(["copyUrl"])
        self.clipboardCopyMenu.addAction(copyUrlAction)
        self.env.pluginAPI.addAction(copyUrlAction)

        self.editMenu.addMenu(self.clipboardCopyMenu)

        self.convertCase = QMenu(QCoreApplication.translate("MainWindow", "Convert Case to"), self)

        convertUppercase = QAction(QCoreApplication.translate("MainWindow", "Uppercase"), self)
        convertUppercase.triggered.connect(lambda: self.getTextEditWidget().replaceSelectedText(self.getTextEditWidget().selectedText().upper()))
        convertUppercase.setData(["convertUppercase"])
        self.convertCase.addAction(convertUppercase)
        self.env.pluginAPI.addAction(convertUppercase)

        convertLowercase = QAction(QCoreApplication.translate("MainWindow", "Lowercase"), self)
        convertLowercase.triggered.connect(lambda: self.getTextEditWidget().setCurrentText(self.getTextEditWidget().getCurrentText().lower()))
        convertLowercase.setData(["convertLowercase"])
        self.convertCase.addAction(convertLowercase)
        self.env.pluginAPI.addAction(convertLowercase)

        convertTitle = QAction(QCoreApplication.translate("MainWindow", "Title"), self)
        convertTitle.triggered.connect(lambda: self.getTextEditWidget().setCurrentText(self.getTextEditWidget().getCurrentText().title()))
        convertTitle.setData(["convertTitle"])
        self.convertCase.addAction(convertTitle)
        self.env.pluginAPI.addAction(convertTitle)

        convertSwap = QAction(QCoreApplication.translate("MainWindow", "Swap"), self)
        convertSwap.triggered.connect(lambda: self.getTextEditWidget().setCurrentText(self.getTextEditWidget().getCurrentText().swapcase()))
        convertSwap.setData(["convertSwap"])
        self.convertCase.addAction(convertSwap)
        self.env.pluginAPI.addAction(convertSwap)

        convertCaseRandomAction = QAction(QCoreApplication.translate("MainWindow", "Random"), self)
        convertCaseRandomAction.triggered.connect(self.convertCaseRandom)
        convertCaseRandomAction.setData(["convertCaseRandom"])
        self.convertCase.addAction(convertCaseRandomAction)
        self.env.pluginAPI.addAction(convertCaseRandomAction)

        self.editMenu.addMenu(self.convertCase)

        self.lineOperationsMenu = QMenu(QCoreApplication.translate("MainWindow", "Line operations"), self)

        duplicateCurrentLineAction = QAction(QCoreApplication.translate("MainWindow", "Duplicate Current Line"), self)
        duplicateCurrentLineAction.triggered.connect(self.duplicateCurrentLine)
        duplicateCurrentLineAction.setData(["duplicateCurrentLine"])
        self.lineOperationsMenu.addAction(duplicateCurrentLineAction)
        self.env.pluginAPI.addAction(duplicateCurrentLineAction)

        deleteCurrentLineAction = QAction(QCoreApplication.translate("MainWindow", "Delete Current Line"), self)
        deleteCurrentLineAction.triggered.connect(self.removeCurrentLine)
        deleteCurrentLineAction.setData(["removeCurrentLine"])
        self.lineOperationsMenu.addAction(deleteCurrentLineAction)
        self.env.pluginAPI.addAction(deleteCurrentLineAction)

        sortAlphabetical = QAction(QCoreApplication.translate("MainWindow", "Sort lines alphabetically"), self)
        sortAlphabetical.triggered.connect(self.sortLinesAlphabetical)
        sortAlphabetical.setData(["sortAlphabetical"])
        self.lineOperationsMenu.addAction(sortAlphabetical)
        self.env.pluginAPI.addAction(sortAlphabetical)

        shuffleLinesAction = QAction(QCoreApplication.translate("MainWindow", "Shuffle Lines"), self)
        shuffleLinesAction.triggered.connect(self.shuffleLines)
        shuffleLinesAction.setData(["shuffleLines"])
        self.lineOperationsMenu.addAction(shuffleLinesAction)
        self.env.pluginAPI.addAction(shuffleLinesAction)

        self.editMenu.addMenu(self.lineOperationsMenu)

        self.eolModeMenu = QMenu(QCoreApplication.translate("MainWindow", "End of line"), self)

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

        self.viewMenu = self.menubar.addMenu(QCoreApplication.translate("MainWindow", "&View"))

        self.zoomMenu = QMenu(QCoreApplication.translate("MainWindow", "Zoom"), self)

        zoomIn = QAction(QCoreApplication.translate("MainWindow", "Zoom in"), self)
        zoomIn.setIcon(getThemeIcon(self.env, "zoom-in"))
        zoomIn.triggered.connect(lambda: self.getTextEditWidget().zoomIn())
        zoomIn.setData(["zoomIn"])
        self.zoomMenu.addAction(zoomIn)
        self.env.pluginAPI.addAction(zoomIn)

        zoomOut = QAction(QCoreApplication.translate("MainWindow", "Zoom out"), self)
        zoomOut.setIcon(getThemeIcon(self.env, "zoom-out"))
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

        zoomDefault = QAction(QCoreApplication.translate("MainWindow", "Default Zoom"), self)
        zoomDefault.setIcon(getThemeIcon(self.env, "zoom-original"))
        zoomDefault.triggered.connect(lambda: self.getTextEditWidget().zoomTo(self.env.settings.defaultZoom))
        zoomDefault.setData(["zoomDefault"])
        self.zoomMenu.addAction(zoomDefault)
        self.env.pluginAPI.addAction(zoomDefault)

        zoomCustom = QAction(QCoreApplication.translate("MainWindow", "Custom"), self)
        zoomCustom.triggered.connect(self.setCustomZoom)
        zoomCustom.setData(["zoomCustom"])
        self.zoomMenu.addAction(zoomCustom)
        self.env.pluginAPI.addAction(zoomCustom)

        self.viewMenu.addMenu(self.zoomMenu)

        self.fullscreenAction = QAction(QCoreApplication.translate("MainWindow", "Fullscreen"), self)
        self.fullscreenAction.triggered.connect(self.fullscreenMenuBarClicked)
        self.fullscreenAction.setData(["fullscreen"])
        self.fullscreenAction.setCheckable(True)
        self.viewMenu.addAction(self.fullscreenAction)
        self.env.pluginAPI.addAction(self.fullscreenAction)

        self.toggleSidebarAction = QAction(QCoreApplication.translate("MainWindow", "Sidebar"), self)
        self.toggleSidebarAction.triggered.connect(self.toggleSidebarClicked)
        self.toggleSidebarAction.setData(["toggleSidebar"])
        self.toggleSidebarAction.setCheckable(True)
        self.viewMenu.addAction(self.toggleSidebarAction)
        self.env.pluginAPI.addAction(self.toggleSidebarAction)

        self.viewMenu.addSeparator()

        foldAllAction = QAction(QCoreApplication.translate("MainWindow", "Fold All"), self)
        foldAllAction.triggered.connect(lambda: self.getTextEditWidget().SendScintilla(QsciScintillaBase.SCI_FOLDALL,0))
        foldAllAction.setData(["foldAll"])
        self.viewMenu.addAction(foldAllAction)
        self.env.pluginAPI.addAction(foldAllAction)

        unfoldAllAction = QAction(QCoreApplication.translate("MainWindow", "Unfold All"), self)
        unfoldAllAction.triggered.connect(lambda: self.getTextEditWidget().SendScintilla(QsciScintillaBase.SCI_FOLDALL,1))
        unfoldAllAction.setData(["unfoldAll"])
        self.viewMenu.addAction(unfoldAllAction)
        self.env.pluginAPI.addAction(unfoldAllAction)

        self.viewMenu.addSeparator()

        self.splitViewMenu = QMenu(QCoreApplication.translate("MainWindow", "Split View"), self)

        splitVerticalAction = QAction(QCoreApplication.translate("MainWindow", "Split Vertical"), self)
        splitVerticalAction.triggered.connect(lambda: self.splitViewWidget.splitVertical())
        splitVerticalAction.setData(["splitVertical"])
        self.splitViewMenu.addAction(splitVerticalAction)
        self.env.pluginAPI.addAction(splitVerticalAction)

        self.deleteCurrentViewAction = QAction(QCoreApplication.translate("MainWindow", "Close Current View"), self)
        self.deleteCurrentViewAction.triggered.connect(lambda: self.splitViewWidget.deleteCurrentView())
        self.deleteCurrentViewAction.setData(["deleteCurrentView"])
        self.deleteCurrentViewAction.setEnabled(False)
        self.splitViewMenu.addAction(self.deleteCurrentViewAction)
        self.env.pluginAPI.addAction(self.deleteCurrentViewAction)

        self.viewMenu.addMenu(self.splitViewMenu)

        self.searchmenu = self.menubar.addMenu(QCoreApplication.translate("MainWindow", "&Search"))

        search = QAction(QCoreApplication.translate("MainWindow", "&Find"), self)
        search.setIcon(getThemeIcon(self.env, "edit-find"))
        search.triggered.connect(lambda: self.getTabWidget().currentWidget().showSearchBar())
        search.setData(["find"])
        self.searchmenu.addAction(search)
        self.env.pluginAPI.addAction(search)

        advancedSearch = QAction(QCoreApplication.translate("MainWindow", "Advanced Search"), self)
        advancedSearch.setIcon(getThemeIcon(self.env, "edit-find"))
        advancedSearch.triggered.connect(lambda: self.env.searchWindow.openWindow(self.getTextEditWidget()))
        self.searchmenu.addAction(advancedSearch)
        self.env.pluginAPI.addAction(advancedSearch)

        searchAndReplace = QAction(QCoreApplication.translate("MainWindow", "&Find and Replace"), self)
        searchAndReplace.setIcon(getThemeIcon(self.env, "edit-find-replace"))
        searchAndReplace.triggered.connect(lambda: self.env.searchReplaceWindow.display(self.getTextEditWidget()))
        searchAndReplace.setData(["findReplaceWindow"])
        self.searchmenu.addAction(searchAndReplace)
        self.env.pluginAPI.addAction(searchAndReplace)

        gotoLine = QAction(QCoreApplication.translate("MainWindow", "Goto Line"), self)
        gotoLine.triggered.connect(lambda: self.env.gotoLineWindow.openWindow(self.getTextEditWidget()))
        gotoLine.setData(["gotoLine"])
        self.searchmenu.addAction(gotoLine)
        self.env.pluginAPI.addAction(gotoLine)

        self.toolsMenu = self.menubar.addMenu(QCoreApplication.translate("MainWindow", "&Tools"))

        pickColor = QAction(QCoreApplication.translate("MainWindow", "Pick Color"), self)
        pickColor.triggered.connect(self.pickColorClicked)
        pickColor.setData(["pickColor"])
        self.toolsMenu.addAction(pickColor)
        self.env.pluginAPI.addAction(pickColor)

        documentStatistics = QAction(QCoreApplication.translate("MainWindow", "&Document Statistics"), self)
        documentStatistics.triggered.connect(lambda: self.env.documentStatistics.openWindow(self.getTextEditWidget()))
        documentStatistics.setData(["documentStatistics"])
        self.toolsMenu.addAction(documentStatistics)
        self.env.pluginAPI.addAction(documentStatistics)

        insertDateTime = QAction(QCoreApplication.translate("MainWindow", "&Insert Date and Time"), self)
        insertDateTime.triggered.connect(lambda: self.env.dateTimeWindow.openWindow(self.getTextEditWidget()))
        insertDateTime.setData(["insertDateTime"])
        self.toolsMenu.addAction(insertDateTime)
        self.env.pluginAPI.addAction(insertDateTime)

        self.toolsMenu.addSeparator()

        stripSpacesAction = QAction(QCoreApplication.translate("MainWindow", "Strip Trailing Spaces"), self)
        stripSpacesAction.triggered.connect(self.stripSpaces)
        stripSpacesAction.setData(["stripSpaces"])
        self.toolsMenu.addAction(stripSpacesAction)
        self.env.pluginAPI.addAction(stripSpacesAction)

        replaceTabSpacesAction = QAction(QCoreApplication.translate("MainWindow", "Replace Tabs with Spaces"), self)
        replaceTabSpacesAction.triggered.connect(self.replaceTabSpaces)
        replaceTabSpacesAction.setData(["replaceTabSpaces"])
        self.toolsMenu.addAction(replaceTabSpacesAction)
        self.env.pluginAPI.addAction(replaceTabSpacesAction)

        replaceSpacesTabAction = QAction(QCoreApplication.translate("MainWindow", "Replace Spaces with Tabs"), self)
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

        self.settingsMenu = self.menubar.addMenu(QCoreApplication.translate("MainWindow", "Settings"))

        settingsAction = QAction(QCoreApplication.translate("MainWindow", "&Settings"), self)
        settingsAction.setIcon(getThemeIcon(self.env, "preferences-other"))
        settingsAction.triggered.connect(lambda: self.env.settingsWindow.openWindow())
        settingsAction.setData(["settings"])
        self.settingsMenu.addAction(settingsAction)
        self.env.pluginAPI.addAction(settingsAction)

        overwriteLanguageAction = QAction(QCoreApplication.translate("MainWindow", "Manage languages"))
        overwriteLanguageAction.triggered.connect(lambda: LanguageOverwritesWindow(self.env).exec())
        overwriteLanguageAction .setData(["overwriteLanguage"])
        self.settingsMenu.addAction(overwriteLanguageAction )
        self.env.pluginAPI.addAction(overwriteLanguageAction )

        editThemesAction = QAction(QCoreApplication.translate("MainWindow", "Manage custom themes"), self)
        editThemesAction.triggered.connect(lambda: ManageThemeListWindow(self.env).exec())
        editThemesAction.setData(["editThemes"])
        self.settingsMenu.addAction(editThemesAction)
        self.env.pluginAPI.addAction(editThemesAction)

        self.settingsMenu.addSeparator()

        exportDataAction = QAction(QCoreApplication.translate("MainWindow", "Export data"))
        exportDataAction.triggered.connect(lambda: ExportDataWindow(self.env).exec())
        exportDataAction.setData(["exportData"])
        self.settingsMenu.addAction(exportDataAction)
        self.env.pluginAPI.addAction(exportDataAction)

        importDataAction = QAction(QCoreApplication.translate("MainWindow", "Import data"))
        importDataAction.triggered.connect(self._importDataClicked)
        importDataAction.setData(["importData"])
        self.settingsMenu.addAction(importDataAction)
        self.env.pluginAPI.addAction(importDataAction)

        self.languageMenu = self.menubar.addMenu(QCoreApplication.translate("MainWindow", "&Language"))

        #self.updateLanguageMenu()

        self.encodingMenu = self.menubar.addMenu(QCoreApplication.translate("MainWindow", "Encoding"))
        self.updateEncodingMenu()

        self.bookmarkMenu = self.menubar.addMenu(QCoreApplication.translate("MainWindow", "Bookmarks"))

        addRemoveBookmarkAction = QAction(QCoreApplication.translate("MainWindow", "Set/delete bookmark"), self)
        addRemoveBookmarkAction.triggered.connect(self.addRemoveBookmark)
        addRemoveBookmarkAction.setData(["addRemoveBookmark"])
        self.bookmarkMenu.addAction(addRemoveBookmarkAction)
        self.env.pluginAPI.addAction(addRemoveBookmarkAction)

        nextBookmarkAction = QAction(QCoreApplication.translate("MainWindow", "Next bookmark"), self)
        nextBookmarkAction.triggered.connect(self.nextBookmark)
        nextBookmarkAction.setData(["nextBookmark"])
        self.bookmarkMenu.addAction(nextBookmarkAction)
        self.env.pluginAPI.addAction(nextBookmarkAction)

        previousBookmarkAction = QAction(QCoreApplication.translate("MainWindow", "Previous bookmark"), self)
        previousBookmarkAction.triggered.connect(self.previousBookmark)
        previousBookmarkAction.setData(["previousBookmark"])
        self.bookmarkMenu.addAction(previousBookmarkAction)
        self.env.pluginAPI.addAction(previousBookmarkAction)

        clearBookmarksAction = QAction(QCoreApplication.translate("MainWindow", "Clear all bookmarks"), self)
        clearBookmarksAction.triggered.connect(self.clearBookmarks)
        clearBookmarksAction.setData(["clearBookmarks"])
        self.bookmarkMenu.addAction(clearBookmarksAction)
        self.env.pluginAPI.addAction(clearBookmarksAction)

        self.macroMenu = self.menubar.addMenu(QCoreApplication.translate("MainWindow", "Macros"))

        self.recordMacroAction = QAction(QCoreApplication.translate("MainWindow", "Start recording"), self)
        self.recordMacroAction.triggered.connect(self.startMacroRecording)
        self.recordMacroAction.setData(["recordMacro"])
        self.env.pluginAPI.addAction(self.recordMacroAction)

        self.stopMacroAction = QAction(QCoreApplication.translate("MainWindow", "Stop recording"), self)
        self.stopMacroAction.triggered.connect(self.stopMacroRecording)
        self.stopMacroAction.setData(["stopMacro"])
        self.env.pluginAPI.addAction(self.stopMacroAction)
        self.stopMacroAction.setEnabled(False)

        self.playMacroAction = QAction(QCoreApplication.translate("MainWindow", "Execute macro"), self)
        self.playMacroAction.triggered.connect(self.playMacro)
        self.playMacroAction.setData(["playMacro"])
        self.env.pluginAPI.addAction(self.playMacroAction)
        self.playMacroAction.setEnabled(False)

        self.saveMacroAction = QAction(QCoreApplication.translate("MainWindow", "Save macro"), self)
        self.saveMacroAction.triggered.connect(self.saveMacro)
        self.saveMacroAction.setData(["saveMacro"])
        self.env.pluginAPI.addAction(self.saveMacroAction)
        self.saveMacroAction.setEnabled(False)

        self.manageMacrosAction = QAction(QCoreApplication.translate("MainWindow", "Manage Macros"), self)
        self.manageMacrosAction.triggered.connect(lambda: self.env.manageMacrosWindow.openWindow())
        self.manageMacrosAction.setData(["manageMacros"])
        self.env.pluginAPI.addAction(self.manageMacrosAction)

        self.updateMacroMenu()

        self.executeMenu = self.menubar.addMenu(QCoreApplication.translate("MainWindow", "Execute"))

        self.executeCommandAction = QAction(QCoreApplication.translate("MainWindow", "Execute Command"), self)
        self.executeCommandAction.triggered.connect(lambda: self.env.executeCommandWindow.openWindow(self.getTextEditWidget()))
        self.executeCommandAction.setData(["executeCommand"])
        self.env.pluginAPI.addAction(self.executeCommandAction)

        self.editCommandsAction = QAction(QCoreApplication.translate("MainWindow", "Edit Commands"), self)
        self.editCommandsAction.triggered.connect(lambda: self.env.editCommandsWindow.openWindow())
        self.editCommandsAction.setData(["editCommands"])
        self.env.pluginAPI.addAction(self.editCommandsAction)

        self.updateExecuteMenu()

        self.aboutMenu = self.menubar.addMenu("&?")

        searchAction = QAction(QCoreApplication.translate("MainWindow", "Search Action"), self)
        searchAction.triggered.connect(lambda: self.env.actionSearchWindow.openWindow())
        searchAction.setData(["searchAction"])
        self.aboutMenu.addAction(searchAction)
        self.env.pluginAPI.addAction(searchAction)

        self.aboutMenu.addSeparator()

        openDataFolder = QAction(QCoreApplication.translate("MainWindow", "Open data directory"), self)
        openDataFolder.triggered.connect(lambda: openFileDefault(self.env.dataDir))
        openDataFolder.setData(["openDataFolder"])
        self.aboutMenu.addAction(openDataFolder)
        self.env.pluginAPI.addAction(openDataFolder)

        openProgramFolder = QAction(QCoreApplication.translate("MainWindow", "Open program directory"), self)
        openProgramFolder.triggered.connect(lambda: openFileDefault(self.env.programDir))
        openProgramFolder.setData(["openProgramFolder"])
        self.aboutMenu.addAction(openProgramFolder)
        self.env.pluginAPI.addAction(openProgramFolder)

        if self.env.enableUpdater:
            searchForUpdatesAction = QAction(QCoreApplication.translate("MainWindow", "Search for Updates"), self)
            searchForUpdatesAction.triggered.connect(lambda: searchForUpdates(self, self.env, False))
            searchForUpdatesAction.setData(["searchForUpdates"])
            self.aboutMenu.addAction(searchForUpdatesAction)
            self.env.pluginAPI.addAction(searchForUpdatesAction)

        showDayTip = QAction(QCoreApplication.translate("MainWindow", "Tip of the Day"), self)
        showDayTip.triggered.connect(lambda: self.env.dayTipWindow.openWindow())
        showDayTip.setData(["showDayTip"])
        self.aboutMenu.addAction(showDayTip)
        self.env.pluginAPI.addAction(showDayTip)

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

        viewSourceAction = QAction(QCoreApplication.translate("MainWindow", "View Source"), self)
        viewSourceAction.triggered.connect(lambda: webbrowser.open("https://codeberg.org/JakobDev/jdTextEdit"))
        viewSourceAction.setData(["viewSource"])
        self.aboutMenu.addAction(viewSourceAction)
        self.env.pluginAPI.addAction(viewSourceAction)

        reportBugAction = QAction(QCoreApplication.translate("MainWindow", "Report Bug"), self)
        reportBugAction.triggered.connect(lambda: webbrowser.open("https://codeberg.org/JakobDev/jdTextEdit/issues"))
        reportBugAction.setData(["reportBug"])
        self.aboutMenu.addAction(reportBugAction)
        self.env.pluginAPI.addAction(reportBugAction)

        viewDocumentationAction = QAction(QCoreApplication.translate("MainWindow", "View Documentation"), self)
        viewDocumentationAction.triggered.connect(lambda: webbrowser.open("https://jdtextedit.readthedocs.io"))
        viewDocumentationAction.setData(["viewDocumentation"])
        self.aboutMenu.addAction(viewDocumentationAction)
        self.env.pluginAPI.addAction(viewDocumentationAction)

        donateAction = QAction(QCoreApplication.translate("MainWindow", "Donate"), self)
        donateAction.triggered.connect(lambda: webbrowser.open("https://ko-fi.com/jakobdev"))
        donateAction.setData(["donate"])
        self.aboutMenu.addAction(donateAction)
        self.env.pluginAPI.addAction(donateAction)

        self.aboutMenu.addSeparator()

        about = QAction(QCoreApplication.translate("MainWindow", "About"), self)
        about.triggered.connect(lambda: self.env.aboutWindow.show())
        about.setData(["about"])
        self.aboutMenu.addAction(about)
        self.env.pluginAPI.addAction(about)

        aboutQt = QAction(QCoreApplication.translate("MainWindow", "About Qt"), self)
        aboutQt.triggered.connect(QApplication.instance().aboutQt)
        aboutQt.setData(["aboutQt"])
        self.aboutMenu.addAction(aboutQt)
        self.env.pluginAPI.addAction(aboutQt)

        self.updateRecentFilesMenu()
        separator = QAction(QCoreApplication.translate("MainWindow", "Seperator"))
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
            empty = QAction(QCoreApplication.translate("MainWindow", "No Templates found"), self)
            empty.setEnabled(False)
            self.templateMenu.addAction(empty)
        else:
            for i in self.env.templates:
                templateAction = QAction(i[0],self)
                templateAction.setData([False, i[1]])
                templateAction.triggered.connect(self.openTemplate)
                self.templateMenu.addAction(templateAction)

        self.templateMenu.addSeparator()
        addMenu = self.templateMenu.addMenu(QCoreApplication.translate("MainWindow", "Add"))

        addCurrentDocumentAction = QAction(QCoreApplication.translate("MainWindow", "Save current document as template"), self)
        addCurrentDocumentAction.triggered.connect(self.addCurrentDocumentTemplate)
        addMenu.addAction(addCurrentDocumentAction)

        addFileAction = QAction(QCoreApplication.translate("MainWindow", "Add file as template"),self)
        addFileAction.triggered.connect(self.addFileTemplate)
        addMenu.addAction(addFileAction)

        manageAction = QAction(QCoreApplication.translate("MainWindow", "Manage"), self)
        manageAction.triggered.connect(self._manageTemplatesClicked)
        self.templateMenu.addAction(manageAction)

    def openTemplate(self):
        action = self.sender()
        if action:
            self.openFile(action.data()[1], template=True)

    def addCurrentDocumentTemplate(self):
        """
        This function is called when the user clicks on Templates>Add>Save Document as Template
        """
        name, ok = QInputDialog.getText(self, QCoreApplication.translate("MainWindow", "Enter name"), QCoreApplication.translate("MainWindow", "Please enter a name for the template"))
        if not ok or name == "":
            return
        if not isFilenameValid(name):
            showMessageBox(QCoreApplication.translate("MainWindow", "Invalid filename"), QCoreApplication.translate("MainWindow", "The Filename is invalid"))
            return
        path = os.path.join(self.env.dataDir, "templates", name)
        self.saveFile(self.getTextEditWidget(), path=path, template=True)
        self.env.templates.append([name, path])
        self.updateTemplateMenu()

    def addFileTemplate(self):
        """
        This function is called when the user clicks on Templates>Add>Add file as template
        """
        original_path = QFileDialog.getOpenFileName(self)
        if not original_path[0]:
            return

        name, ok = QInputDialog.getText(self, QCoreApplication.translate("MainWindow", "Enter name"), QCoreApplication.translate("MainWindow", "Please enter a name for the template"))
        if not ok or name == "":
            return

        if not isFilenameValid(name):
            showMessageBox(QCoreApplication.translate("MainWindow", "Invalid filename"), QCoreApplication.translate("MainWindow", "The Filename is invalid"))
            return

        template_path = os.path.join(self.env.dataDir, "templates", name)
        shutil.copyfile(original_path[0], template_path)
        self.env.templates.append([name, template_path])
        self.updateTemplateMenu()

    def _manageTemplatesClicked(self):
        ManageTemplatesWindow(self.env).openWindow(self)

    def updateRecentFilesMenu(self):
        self.recentFilesMenu.clear()

        if len(self.env.recentFiles) == 0:
            empty = QAction(QCoreApplication.translate("MainWindow", "No recent files"), self)
            empty.setEnabled(False)
            self.recentFilesMenu.addAction(empty)
        else:
            count = 1
            for i in self.env.recentFiles:
                fileItem = QAction(str(count) + ". " + i, self)
                fileItem.setData([False,i])
                fileItem.triggered.connect(self.openRecentFile)
                self.recentFilesMenu.addAction(fileItem)
                count += 1
            self.recentFilesMenu.addSeparator()
            clear = QAction(QCoreApplication.translate("MainWindow", "Clear"), self)
            clear.triggered.connect(self.clearRecentFiles)
            self.recentFilesMenu.addAction(clear)
            openAll = QAction(QCoreApplication.translate("MainWindow", "Open all"), self)
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
        self.env.fileNameFilters = QCoreApplication.translate("MainWindow", "All files") + " (*);;"
        self.languageMenu.clear()
        alphabet = {}
        for i in self.env.languageList:
            startLetter = i.getName()[0].upper()
            if startLetter not in alphabet:
                alphabet[startLetter] = []
            alphabet[startLetter].append(i)
        for c in ascii_uppercase:
            if c in alphabet:
                letterMenu = QMenu(c, self)
                for i in alphabet[c]:
                    languageAction = QAction(i.getName(), self)
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
        noneAction = QAction(QCoreApplication.translate("MainWindow", "Plain Text"), self)
        noneAction.triggered.connect(self.languagePlainTextClicked)
        noneAction.setCheckable(True)
        self.env.languagePlainTextAction = noneAction
        self.languageMenu.addAction(noneAction)
        self.env.fileNameFilters = self.env.fileNameFilters + QCoreApplication.translate("MainWindow", "Plain Text") + " (*.txt)"
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

    def updateMacroMenu(self) -> None:
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
            singleMacroAction.setData([None, i["macro"]])
            self.macroMenu.addAction(singleMacroAction)

    def playMenuMacro(self) -> None:
        action = self.sender()
        if action:
            macro = QsciMacro(self.getTextEditWidget())
            macro.load(action.data()[1])
            macro.play()

    def updateExecuteMenu(self) -> None:
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

    def openFile(self, path: str, template: bool = False, reload: bool = False) -> None:
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
            filehandle = open(path, "rb")
        except PermissionError:
            showMessageBox(QCoreApplication.translate("MainWindow", "Can't open file"), QCoreApplication.translate("MainWindow", "You don't have the permission to open {{path}}").replace("{{path}}", path))
            return
        except Exception as e:
            self.env.logger.exception(e)
            showMessageBox(QCoreApplication.translate("MainWindow", "Unknown error"), QCoreApplication.translate("MainWindow", "An unknown error has occurred"))
            return

        fileBytes = filehandle.read()
        if len(fileBytes) >= self.env.settings.bigFileSize and self.env.settings.enableBigFileLimit:
            isBigFile = True
        else:
            isBigFile = False
        if self.env.settings.detectEncoding and not(isBigFile and self.env.settings.bigFileDisableEncodingDetect):
            if self.env.settings.get("encodingDetectLib") in self.env.encodingDetectFunctions:
                encoding = self.env.encodingDetectFunctions[self.env.settings.get("encodingDetectLib")](fileBytes)["encoding"]
                if not encoding:
                    encoding = "UTF-8"
                elif encoding == "ascii":
                    encoding = "UTF-8"
                for i in getEncodingList():
                    if encoding in i:
                        encoding = i[0]
            else:
                self.env.logger.error("Encoding detection module " + self.env.settings.get("encodingDetectLib") + " was not found")
                encoding = self.env.settings.get("defaultEncoding")
        else:
            encoding = self.env.settings.get("defaultEncoding")

        try:
            fileContent = fileBytes.decode(encoding)
            encodingError = False
        except UnicodeDecodeError:
            fileContent = fileBytes.decode(encoding, errors="replace")
            encodingError = True

        filehandle.close()
        tabWidget = self.getTabWidget()
        if (not self.getTextEditWidget().isNew) and (not reload):
            tabWidget.createTab(QCoreApplication.translate("MainWindow", "Untitled"), focus=True)
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
            for i in self.env.languageList:
                languageOverwrite = self.env.languageOverwrites.get(i.getID(), {})

                if "extensions" in languageOverwrite and languageOverwrite["extensions"]["enabled"]:
                    extensions = languageOverwrite["extensions"]["textList"]
                else:
                    extensions = i.getExtensions()

                if "starttext" in languageOverwrite and languageOverwrite["starttext"]["enabled"]:
                    starttext = languageOverwrite["starttext"]["textList"]
                else:
                    starttext = i.getStarttext()

                if "mimetypes" in languageOverwrite and languageOverwrite["mimetypes"]["enabled"]:
                    mimetypes= languageOverwrite["mimetypes"]["textList"]
                else:
                    mimetypes = i.getMimeType()

                foundExtension = False

                for e in extensions:
                    if path.endswith(e):
                        foundExtension = True
                        editWidget.setLanguage(i)
                        break

                if foundExtension:
                    break

                foundStarttext = False

                for e in starttext:
                    if fileContent.startswith(e):
                        foundStarttext = True
                        editWidget.setLanguage(i)
                        break

                if foundStarttext:
                    break

                if self.env.mimeDatabase.mimeTypeForFile(path).name() in mimetypes:
                    editWidget.setLanguage(i)
                    break

        containerWidget.clearBanner()
        if self.env.settings.useEditorConfig and not template:
            editWidget.loadEditorConfig()
        if editWidget.settings.defaultEncoding != encoding and self.env.settings.showEncodingBanner:
            containerWidget.showBanner(WrongEncodingBanner(self.env, containerWidget))
        if self.env.settings.showEolBanner:
            if editWidget.eolMode() == QsciScintilla.EolMode.EolWindows and editWidget.settings.defaultEolMode != 0:
                containerWidget.showBanner(WrongEolBanner(containerWidget))
            elif editWidget.eolMode() == QsciScintilla.EolMode.EolUnix and editWidget.settings.defaultEolMode != 1:
                containerWidget.showBanner(WrongEolBanner(containerWidget))
            elif editWidget.eolMode() == QsciScintilla.EolMode.EolMac and editWidget.settings.defaultEolMode != 2:
                containerWidget.showBanner(WrongEolBanner(containerWidget))
        if isBigFile and self.env.settings.bigFileShowBanner:
            containerWidget.showBanner(BigFileBanner(containerWidget))
        if encodingError:
            containerWidget.showBanner(SimpleMessageBanner(containerWidget, QCoreApplication.translate("MainWindow", "This file has some decoding errors")))
        self.env.editorSignals.openFile.emit(editWidget)
        tabWidget.setActive()

    def saveFile(self, editWidget: CodeEdit, path: Optional[str] = None, template: bool = False) -> None:
        containerWidget = editWidget.container

        if not path:
            path = editWidget.getFilePath()

        if not template:
            containerWidget.fileWatcher.removePath(path)
            if os.path.isfile(path) and self.env.settings.get("saveBackupEnabled"):
                shutil.copyfile(path, path + self.env.settings.get("saveBackupExtension"))

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

        text = text.encode(editWidget.getUsedEncoding(), errors="replace")

        try:
            filehandle = open(path, "wb")
        except PermissionError:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Can't save file"), QCoreApplication.translate("MainWindow", "You don't have the permission to write {{path}}").replace("{{path}}", editWidget.getFilePath()))
            return
        except Exception as e:
            self.env.logger.exception(e)
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Unknown error"), QCoreApplication.translate("MainWindow", "An unknown error has occurred"))
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
            for i in self.env.languageList:
                for e in i.getExtensions():
                    if path.endswith(e):
                        editWidget.setLanguage(i)
                        break
                else:
                    break

                for e in i.getStarttext():
                    if text.startswith(e.encode("utf-8")):
                        editWidget.setLanguage(i)
                        break
                else:
                    break

                if self.env.mimeDatabase.mimeTypeForFile(path).name() in i.getMimeType():
                    editWidget.setLanguage(i)
                    break

    def newMenuBarClicked(self):
        self.getTabWidget().createTab(QCoreApplication.translate("MainWindow", "Untitled"), focus=True)

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

        path = QFileDialog.getOpenFileName(self, QCoreApplication.translate("MainWindow", "Open"), startPath, self.env.fileNameFilters)
        if path[0]:
            self.openFile(path[0])
            self.env.lastOpenPath = path[0]

    def openDirectoryMenuBarClicked(self):
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

        path = QFileDialog.getExistingDirectory(self, QCoreApplication.translate("MainWindow", "Open Directory"), startPath)
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

    def saveAsMenuBarClicked(self, editWidget: CodeEdit) -> None:
        pathTypeSetting = self.env.settings.get("saveFilePathType")
        if pathTypeSetting == 0:
            # Use path of current file
            startPath = os.path.dirname(editWidget.getFilePath())
        elif pathTypeSetting == 1:
            # Use latest Path
            startPath = self.env.lastSavePath
        elif pathTypeSetting == 2:
            # Use custom path
            startPath = self.env.settings.get("saveFileCustomPath")
        path = QFileDialog.getSaveFileName(self, QCoreApplication.translate("MainWindow", "Save as ..."), startPath, self.env.fileNameFilters)

        if path[0]:
            self.getTextEditWidget().setFilePath(path[0])
            self.saveFile(editWidget)
            tabWidget = editWidget.container.getTabWidget()
            tabWidget.setTabText(editWidget.tabid, os.path.basename(path[0]))
            tabWidget.tabsChanged.emit()
            self.updateWindowTitle()
            self.env.lastSavePath = path

    def saveAllMenuBarClicked(self) -> None:
        for tabWidget in self.splitViewWidget.getAllTabWidgets():
            for i in range(tabWidget.count()):
                self.saveMenuBarClicked(tabWidget.widget(i))

    def closeAllTabs(self) -> None:
        for tabWidget in self.splitViewWidget.getAllTabWidgets():
            for i in range(tabWidget.count()-1,-1,-1):
                tabWidget.tabCloseClicked(i,notCloseProgram=True)
        self.splitViewWidget.initTabWidget()
        self.getTabWidget().createTab(QCoreApplication.translate("MainWindow", "Untitled"), focus=True)

    def printMenuBarClicked(self) -> None:
        """
        This function is called when the user clicks File>Print
        :return:
        """
        printer = QsciPrinter()
        dialog = QPrintDialog(printer)
        dialog.setWindowTitle(QCoreApplication.translate("MainWindow", "Print"))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            editWidget = self.getTextEditWidget()
            printer.printRange(editWidget)

    def getCurrentLines(self) -> list[str]:
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

    def replaceCurrentLines(self, lines: list[str]):
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

    def convertCaseRandom(self):
        new_text = ""
        for i in self.getTextEditWidget().getCurrentText():
            if random.randrange(2) == 0:
                new_text += i.lower()
            else:
                new_text += i.upper()
        self.getTextEditWidget().setCurrentText(new_text)

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
        scale,ok = QInputDialog.getInt(self, QCoreApplication.translate("MainWindow", "Custom zoom"), QCoreApplication.translate("MainWindow", "Please enter a value for the zoom in percent"), currentZoom, 0, 300, 10)
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
            text = text.replace("\t", spaceString)
            editWidget.setText(text)
        else:
            text = editWidget.selectedText()
            text = text.replace("\t", spaceString)
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
            text = text.replace(spaceString, "\t")
            editWidget.setText(text)
        else:
            text = editWidget.selectedText()
            text = text.replace(spaceString, "\t")
            editWidget.replaceSelectedText(text)
        editWidget.setCursorPosition(line,0)

    def toggleSidebarClicked(self):
        if self.sidepane.enabled:
            self.sidepane.enabled = False
            self.sidepane.hide()
        else:
            self.sidepane.enabled = True
            self.sidepane.show()
        self.toggleSidebarAction.setChecked(self.sidepane.enabled)

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
        name, ok = QInputDialog.getText(self, QCoreApplication.translate("MainWindow", "Save macro"), sQCoreApplication.translate("MainWindow", "Please enter a name for the macro"))
        if not ok or name == '':
            return
        self.env.macroList.append({"name": name, "macro": self.currentMacro.save(), "shortcut": ""})
        self.updateMacroMenu()
        with open(os.path.join(self.env.dataDir, "macros.json"), "w", encoding="utf-8") as f:
            json.dump(self.env.macroList, f, ensure_ascii=False, indent=4)

    def _importDataClicked(self):
        zipFilterText = QCoreApplication.translate("MainWindow", "Zip Files")
        allFilterText = QCoreApplication.translate("MainWindow", "All Files")

        path = QFileDialog.getOpenFileName(self, filter=f"{zipFilterText} (*.zip);;{allFilterText} (*)")[0]

        if path == "":
            return

        try:
            zf = zipfile.ZipFile(path, "r")
            exportData = json.loads(zf.read("jdTextEditExportData.json").decode("utf-8"))
            assert isinstance(exportData["dateTime"], str)
            assert isinstance(exportData["platform"], str)
            assert isinstance(exportData["version"], str)
            assert isinstance(exportData["dataList"], list)
        except (zipfile.BadZipFile, KeyError, json.decoder.JSONDecodeError, AssertionError):
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Invalid file"), QCoreApplication.translate("MainWindow", "This file does not contains valid exported data from jdTextEdit"))
            try:
                zf.close()
            except UnboundLocalError:
                pass
            return
        except Exception:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Unknown error"), QCoreApplication.translate("MainWindow", "An unknown error happened"))
            return

        text = QCoreApplication.translate("MainWindow", "Are you sure you want to import the following data?") + "<br><br>"

        text += QCoreApplication.translate("MainWindow", "Date and Time: {{DateTime}}").replace("{{DateTime}}", formatDateTime(self.env.settings, datetime.datetime.fromisoformat(exportData["dateTime"]))) + "<br>"
        text += QCoreApplication.translate("MainWindow", "Platform: {{Platform}}").replace("{{Platform}}", exportData["platform"]) + "<br>"
        text += QCoreApplication.translate("MainWindow", "Version: {{Version}}").replace("{{Version}}", exportData["version"]) + "<br><br>"

        text += QCoreApplication.translate("MainWindow", "It includes the following:") + "<br>"
        for i in self.env.exportDataList:
            if i["id"] in exportData["dataList"]:
                text += i["name"] + "<br>"
                exportData["dataList"].remove(i["id"])
        for i in exportData["dataList"]:
            text += i + "<br>"

        text += "<br>" + QCoreApplication.translate("MainWindow", "If you continue, your data will be overwritten and jdTextEdit will be closed")

        if QMessageBox.question(self, QCoreApplication.translate("MainWindow", "Import data"), text) != QMessageBox.StandardButton.Yes:
            zf.close()
            return

        for i in zf.namelist():
            if i == "jdTextEditExportData.json":
                continue
            dataRootPath = os.path.join(self.env.dataDir, i.split("/")[0])
            if os.path.isfile(dataRootPath):
                os.remove(dataRootPath)
            elif os.path.isdir(dataRootPath):
                shutil.rmtree(dataRootPath)
            zf.extract(i, self.env.dataDir)

        zf.close()

        QMessageBox.information(self, QCoreApplication.translate("MainWindow", "Import complete"), QCoreApplication.translate("MainWindow", "The Import is now completed. jdTextEdit will now close."))

        if self.env.settings.get("saveSession"):
            self.saveSession()

        sys.exit(0)

    def deleteAllData(self):
        if QMessageBox.question(self, QCoreApplication.translate("MainWindow", "Delete all data"), QCoreApplication.translate("MainWindow", "This will delete all data of jdTextEdit. After that, jdTextEdit will behave like the first run. jdTexEdit will exit after doing that. Are you sure?")) != QMessageBox.StandardButton.Yes:
            return

        try:
            shutil.rmtree(self.env.dataDir)
        except Exception as e:
            self.env.logger.exception(e)
            showMessageBox(QCoreApplication.translate("MainWindow", "Unknown error"), QCoreApplication.translate("MainWindow", "An unknown error has occurred"))
            return

        sys.exit(0)

    def autoSaveTimeout(self):
        if self.autoSaveTimer.timeout == 0 or not self.env.settings.get("enableAutoSave"):
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
        toolbarPositionList = [Qt.ToolBarArea.TopToolBarArea, Qt.ToolBarArea.BottomToolBarArea, Qt.ToolBarArea.LeftToolBarArea, Qt.ToolBarArea.RightToolBarArea]
        self.addToolBar(toolbarPositionList[settings.toolbarPosition], self.toolbar)
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
        clearStatusBar(self.statusBar())
        for i in settings.get("statusBarWidgetsLeft"):
            try:
                self.statusBar().addWidget(self.env.statusBarWidgetDict[i]())
            except KeyError:
                self.env.logger.error(f"StatusBarWidget with ID {i} not found")
        for i in settings.get("statusBarWidgetsRight"):
            try:
                self.statusBar().addPermanentWidget(self.env.statusBarWidgetDict[i]())
            except KeyError:
                self.env.logger.error(f"StatusBarWidget with ID {i} not found")
        self.updateWindowTitle()
        self.updateStatusBar()

    def updateWindowTitle(self):
        if self.env.settings.get("windowFileTitle"):
            tabWidget = self.getTabWidget()
            self.setWindowTitle(tabWidget.tabText(tabWidget.currentIndex()) + " - jdTextEdit")
        else:
            self.setWindowTitle("jdTextEdit")

    def updateStatusBar(self):
        for i in self.statusBar().children():
            if isinstance(i, StatusBarWidgetBase):
                i.updateWidget(self)

    def saveSession(self):
        if not os.path.isdir(os.path.join(self.env.dataDir, "session_data")):
            os.mkdir(os.path.join(self.env.dataDir, "session_data"))
        data = self.splitViewWidget.getSessionData()
        if self.currentMacro:
            data["currentMacro"] = self.currentMacro.save()
        with open(os.path.join(self.env.dataDir, "session.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def restoreSession(self):
        with open(os.path.join(self.env.dataDir, "session.json"), "r", encoding="utf-8") as f:
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
        self.env.settings.showSidepane = self.sidepane.enabled
        self.env.settings.sidepaneWidget = self.sidepane.content.getSelectedWidget()
        self.env.settings.save(os.path.join(self.env.dataDir, "settings.json"))
        saveProjects(self.env.projects, os.path.join(self.env.dataDir, "projects.json"))
        if self.env.settings.saveWindowState:
            windowState = {}
            saveWindowState(self, windowState, "MainWindow")
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
                os.remove(os.path.join(self.env.dataDir, "windowstate.json"))
            except Exception:
                pass
        with open(os.path.join(self.env.dataDir, "lastversion.txt"), "w", encoding="utf-8") as f:
            f.write(self.env.version)

    def closeEvent(self, event: QCloseEvent):
        self.saveDataClose()
        if self.env.settings.get("saveSession"):
            try:
                self.saveSession()
            except Exception as e:
                self.env.logger.exception(e)
            sys.exit(0)
        else:
            for tabWidget in self.splitViewWidget.getAllTabWidgets():
                for i in range(tabWidget.count()-1, -1, -1):
                    try:
                        tabWidget.tabCloseClicked(i, forceExit=True)
                    except Exception as e:
                        self.env.logger.exception(e)
            event.ignore()

    def removeTempOpenFile(self):
        try:
            os.remove(getTempOpenFilePath())
        except Exception:
            pass

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ingore()

    def dropEvent(self, event: QDropEvent) -> None:
        for i in event.mimeData().urls():
            if i.isLocalFile():
                self.openFile(i.toLocalFile())

    def contextMenuEvent(self, event):
        pass
