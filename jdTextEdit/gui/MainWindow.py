from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QApplication, QLabel, QFileDialog, QStyleFactory, QStyle, QDialog, QColorDialog, QInputDialog
from PyQt5.Qsci import QsciScintilla, QsciScintillaBase, QsciMacro
from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtPrintSupport import QPrintDialog, QPrintPreviewDialog
from PyQt5.Qsci import QsciPrinter
from PyQt5.QtCore import Qt, QFileSystemWatcher, QTimer
from jdTextEdit.Functions import executeCommand, getThemeIcon, openFileDefault, showMessageBox, saveWindowState,restoreWindowState, getTempOpenFilePath
from jdTextEdit.gui.EditTabWidget import EditTabWidget
from jdTextEdit.EncodingList import getEncodingList
from jdTextEdit.gui.DockWidget import DockWidget
from jdTextEdit.Updater import searchForUpdates
from jdTextEdit.gui.BannerWidgets.WrongEncodingBanner import WrongEncodingBanner
from jdTextEdit.gui.BannerWidgets.WrongEolBanner import WrongEolBanner
from jdTextEdit.gui.BannerWidgets.BigFileBanner import BigFileBanner
from string import ascii_uppercase
import webbrowser
import traceback
import requests
import tempfile
import chardet
import shutil
import atexit
import json
import sys
import os
import re

class MainWindow(QMainWindow):
    def __init__(self,env):
        super().__init__()
        self.env = env
        self.currentMacro = None
        self.setupMenubar()
        self.tabWidget = EditTabWidget(env)
        self.setupStatusBar()
        self.toolbar = self.addToolBar("toolbar")
        self.setCentralWidget(self.tabWidget)
        self.autoSaveTimer = QTimer()
        #self.autoSaveTimer.setInterval(2147483647)
        self.autoSaveTimer.timeout.connect(self.autoSaveTimeout)
        if "MainWindow" in env.windowState:
            restoreWindowState(self,env.windowState,"MainWindow")
        else:
            self.setGeometry(0, 0, 800, 600)

    def setup(self):
        #This is called, after all at least
        if os.path.isfile(os.path.join(self.env.dataDir,"session.json")) and not self.env.args["disableSessionRestore"] :
            try:
                self.restoreSession()
            except Exception as e:
                print(traceback.format_exc(),end="")
                showMessageBox("Error","Could not restore session. If jdTextEdit crashes just restart it.")
                os.remove(os.path.join(self.env.dataDir,"session.json"))
                shutil.rmtree(os.path.join(self.env.dataDir,"session_data"))
        else:
            self.tabWidget.createTab(self.env.translate("mainWindow.newTabTitle"))
        self.updateLanguageMenu()
        if len(self.env.args["filename"]) == 1:
            self.openFileCommandline(os.path.abspath(self.env.args["filename"][0]))
        self.getMenuActions(self.menubar)
        self.env.sidepane = DockWidget(self.env)
        self.env.sidepane.hide()
        self.addDockWidget(Qt.LeftDockWidgetArea,self.env.sidepane)
        for i in range(self.tabWidget.count()):
            widget = self.tabWidget.widget(i).getCodeEditWidget()
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
            searchForUpdates(self.env,True)
        if self.env.settings.useIPC:
            open(getTempOpenFilePath(),"w").close()
            self.tempFileOpenWatcher = QFileSystemWatcher()
            self.tempFileOpenWatcher.addPath(getTempOpenFilePath())
            self.tempFileOpenWatcher.fileChanged.connect(self.openTempFileSignal)
            atexit.register(self.removeTempOpenFile)
        self.show()
        #self.getTextEditWidget().ensureCursorVisible()
        if self.env.settings.startupDayTip:
            self.env.dayTipWindow.openWindow()

    def openFileCommandline(self, path):
        if os.path.isfile(path):
            self.openFile(path)
        else:
            #Check if the file is already open but do not exists anymore
            found = False
            for i in range(self.tabWidget.count()):
                if self.tabWidget.widget(i).getCodeEditWidget().getFilePath() == path:
                    self.tabWidget.setCurrentIndex(i)
                    found = True
            if not found:
                if os.path.isdir(path):
                    print("Can't open directory")
                else:
                    self.tabWidget.createTab(os.path.basename(path),focus=True)
                    editWidget = self.getTextEditWidget()
                    editWidget.setFilePath(path)
                    editWidget.isNew = False
                    if self.env.settings.useEditorConfig:
                        editWidget.loadEditorConfig()

    def getTextEditWidget(self):
        return self.tabWidget.currentWidget().getCodeEditWidget()

    def openTempFileSignal(self,path):
        if os.path.getsize(path) == 0:
            return
        with open(path) as f:
            lines = f.read().splitlines()
        if lines[0] == "openFile":
            self.openFileCommandline(lines[1])
        open(path,"w").close()
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
        self.menubar = self.menuBar()
        self.recentFilesMenu = QMenu(self.env.translate("mainWindow.menu.openRecent"))
        self.recentFilesMenu.setIcon(getThemeIcon(self.env,"document-open-recent"))

        self.filemenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.file"))

        new = QAction("&" + self.env.translate("mainWindow.menu.file.new"),self)
        new.setIcon(getThemeIcon(self.env,"document-new"))
        new.triggered.connect(self.newMenuBarClicked)
        new.setData(["newFile"])
        self.filemenu.addAction(new)

        self.templateMenu = QMenu(self.env.translate("mainWindow.menu.newTemplate"),self)
        self.templateMenu.setIcon(getThemeIcon(self.env,"document-new"))
        self.updateTemplateMenu()
        self.filemenu.addMenu(self.templateMenu)

        self.filemenu.addSeparator()

        openmenu = QAction("&" + self.env.translate("mainWindow.menu.file.open"),self)
        openmenu.setIcon(getThemeIcon(self.env,"document-open"))
        openmenu.triggered.connect(self.openMenuBarClicked)
        openmenu.setData(["openFile"])
        self.filemenu.addAction(openmenu)

        openDirectoryMenu = QAction(self.env.translate("mainWindow.menu.file.openDirectory"),self)
        openDirectoryMenu.setIcon(getThemeIcon(self.env,"folder-open"))
        openDirectoryMenu.triggered.connect(self.openDirectoryMenuBarClicked)
        openDirectoryMenu.setData(["directoryOpen"])
        self.filemenu.addAction(openDirectoryMenu)

        self.filemenu.addMenu(self.recentFilesMenu)

        self.filemenu.addSeparator()

        save = QAction("&" + self.env.translate("mainWindow.menu.file.save"),self)
        save.setIcon(getThemeIcon(self.env,"document-save"))
        save.triggered.connect(lambda: self.saveMenuBarClicked(self.tabWidget.currentIndex()))
        save.setData(["saveFile"])
        self.filemenu.addAction(save)

        saveAs = QAction("&" + self.env.translate("mainWindow.menu.file.saveAs"),self)
        saveAs.setIcon(getThemeIcon(self.env,"document-save-as"))
        saveAs.triggered.connect(lambda: self.saveAsMenuBarClicked(self.tabWidget.currentIndex()))
        saveAs.setData(["saveAsFile"])
        self.filemenu.addAction(saveAs)

        saveAll = QAction(self.env.translate("mainWindow.menu.file.saveAll"),self)
        saveAll.setIcon(getThemeIcon(self.env,"document-save-all"))
        saveAll.triggered.connect(self.saveAllMenuBarClicked)
        saveAll.setData(["saveAll"])
        self.filemenu.addAction(saveAll)

        self.filemenu.addSeparator()

        closeTab = QAction(self.env.translate("mainWindow.menu.file.close"),self)
        closeTab.setIcon(QIcon(os.path.join(self.env.programDir,"icons","document-close.png")))
        closeTab.triggered.connect(lambda: self.tabWidget.tabCloseClicked(self.tabWidget.currentIndex()))
        closeTab.setData(["closeTab"])
        self.filemenu.addAction(closeTab)

        closeAllTabsAction = QAction(self.env.translate("mainWindow.menu.file.closeAllTabs"),self)
        closeAllTabsAction.setIcon(QIcon(os.path.join(self.env.programDir,"icons","document-close-all.png")))
        closeAllTabsAction.triggered.connect(self.closeAllTabs)
        closeAllTabsAction.setData(["closeAllTabs"])
        self.filemenu.addAction(closeAllTabsAction)

        printMenuItem = QAction("&" + self.env.translate("mainWindow.menu.file.print"),self)
        printMenuItem.setIcon(getThemeIcon(self.env,"document-print"))
        printMenuItem.triggered.connect(self.printMenuBarClicked)
        printMenuItem.setData(["print"])
        self.filemenu.addAction(printMenuItem)

        exit = QAction("&" + self.env.translate("mainWindow.menu.file.exit"),self)
        exit.setIcon(getThemeIcon(self.env,"application-exit"))
        exit.triggered.connect(self.close)
        exit.setData(["exit"])
        self.filemenu.addAction(exit)

        self.menubar.addMenu(self.filemenu)
        self.editMenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.edit"))

        self.undoMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.undo"),self)
        self.undoMenubarItem.setIcon(getThemeIcon(self.env,"edit-undo"))
        self.undoMenubarItem.triggered.connect(lambda: self.getTextEditWidget().undo())
        self.undoMenubarItem.setData(["undo"])
        self.editMenu.addAction(self.undoMenubarItem)
        self.undoMenubarItem.setEnabled(False)

        self.redoMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.redo"),self)
        self.redoMenubarItem.setIcon(getThemeIcon(self.env,"edit-redo"))
        self.redoMenubarItem.triggered.connect(lambda: self.getTextEditWidget().redo())
        self.redoMenubarItem.setData(["redo"])
        self.editMenu.addAction(self.redoMenubarItem)
        self.redoMenubarItem.setEnabled(False)

        self.editMenu.addSeparator()

        self.cutMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.cut"),self)
        self.cutMenubarItem.setIcon(getThemeIcon(self.env,"edit-cut"))
        self.cutMenubarItem.triggered.connect(lambda: self.getTextEditWidget().cut())
        self.cutMenubarItem.setData(["cut"])
        self.editMenu.addAction(self.cutMenubarItem)
        self.cutMenubarItem.setEnabled(False)

        self.copyMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.copy"),self)
        self.copyMenubarItem.setIcon(getThemeIcon(self.env,"edit-copy"))
        self.copyMenubarItem.triggered.connect(lambda: self.getTextEditWidget().copy())
        self.copyMenubarItem.setData(["copy"])
        self.editMenu.addAction(self.copyMenubarItem)
        self.copyMenubarItem.setEnabled(False)

        paste = QAction("&" + self.env.translate("mainWindow.menu.edit.paste"),self)
        paste.setIcon(getThemeIcon(self.env,"edit-paste"))
        paste.triggered.connect(lambda: self.getTextEditWidget().paste())
        paste.setData(["paste"])
        self.editMenu.addAction(paste)

        self.deleteMenubarItem = QAction("&" + self.env.translate("mainWindow.menu.edit.delete"),self)
        self.deleteMenubarItem.setIcon(getThemeIcon(self.env,"edit-delete"))
        self.deleteMenubarItem.triggered.connect(lambda: self.getTextEditWidget().removeSelectedText())
        self.deleteMenubarItem.setData(["delete"])
        self.editMenu.addAction(self.deleteMenubarItem)
        self.deleteMenubarItem.setEnabled(False)

        self.editMenu.addSeparator()

        selectAll = QAction("&" + self.env.translate("mainWindow.menu.edit.selectAll"),self)
        selectAll.setIcon(getThemeIcon(self.env,"edit-select-all"))
        selectAll.triggered.connect(lambda: self.getTextEditWidget().selectAll())
        selectAll.setData(["selectAll"])
        self.editMenu.addAction(selectAll)

        self.editMenu.addSeparator()

        self.clipboardCopyMenu = QMenu(self.env.translate("mainWindow.menu.edit.copyClipboard"),self)

        copyPath = QAction(self.env.translate("mainWindow.menu.edit.copyClipboard.copyPath"),self)
        copyPath.triggered.connect(lambda: self.env.clipboard.setText(self.getTextEditWidget().getFilePath()))
        copyPath.setData(["copyPath"])
        self.clipboardCopyMenu.addAction(copyPath)

        copyDirectory = QAction(self.env.translate("mainWindow.menu.edit.copyClipboard.copyDirectory"),self)
        copyDirectory.triggered.connect(lambda: self.env.clipboard.setText(os.path.dirname(self.getTextEditWidget().getFilePath())))
        copyDirectory.setData(["copyDirectory"])
        self.clipboardCopyMenu.addAction(copyDirectory)

        copyFilename = QAction(self.env.translate("mainWindow.menu.edit.copyClipboard.copyFilename"),self)
        copyFilename.triggered.connect(lambda: self.env.clipboard.setText(os.path.basename(self.getTextEditWidget().getFilePath())))
        copyFilename.setData(["copyFilename"])
        self.clipboardCopyMenu.addAction(copyFilename)

        self.editMenu.addMenu(self.clipboardCopyMenu)

        self.convertCase = QMenu(self.env.translate("mainWindow.menu.edit.convertCase"),self)

        convertUppercase = QAction(self.env.translate("mainWindow.menu.edit.convertCase.uppercase"),self)
        convertUppercase.triggered.connect(lambda: self.getTextEditWidget().replaceSelectedText(self.getTextEditWidget().selectedText().upper()))
        convertUppercase.setData(["convertUppercase"])
        self.convertCase.addAction(convertUppercase)

        convertLowercase = QAction(self.env.translate("mainWindow.menu.edit.convertCase.lowercase"),self)
        convertLowercase.triggered.connect(lambda: self.getTextEditWidget().replaceSelectedText(self.getTextEditWidget().selectedText().lower()))
        convertLowercase.setData(["convertLowercase"])
        self.convertCase.addAction(convertLowercase)

        convertTitle = QAction(self.env.translate("mainWindow.menu.edit.convertCase.title"),self)
        convertTitle.triggered.connect(lambda: self.getTextEditWidget().replaceSelectedText(self.getTextEditWidget().selectedText().title()))
        convertTitle.setData(["convertTitle"])
        self.convertCase.addAction(convertTitle)

        convertSwap = QAction(self.env.translate("mainWindow.menu.edit.convertCase.swap"),self)
        convertSwap.triggered.connect(lambda: self.getTextEditWidget().replaceSelectedText(self.getTextEditWidget().selectedText().swapcase()))
        convertSwap.setData(["convertSwap"])
        self.convertCase.addAction(convertSwap)

        self.editMenu.addMenu(self.convertCase)

        self.eolModeMenu = QMenu(self.env.translate("mainWindow.menu.edit.eol"),self)

        self.eolModeWindows = QAction("Windows",self)
        self.eolModeWindows.triggered.connect(lambda: self.getTextEditWidget().changeEolMode(QsciScintilla.EolWindows))
        self.eolModeWindows.setData(["eolModeWindows"])
        self.eolModeWindows.setCheckable(True)
        self.eolModeMenu.addAction(self.eolModeWindows)

        self.eolModeUnix = QAction("Unix",self)
        self.eolModeUnix.triggered.connect(lambda: self.getTextEditWidget().changeEolMode(QsciScintilla.EolUnix))
        self.eolModeUnix.setData(["eolModeWindows"])
        self.eolModeUnix.setCheckable(True)
        self.eolModeMenu.addAction(self.eolModeUnix)

        self.eolModeMac = QAction("Mac",self)
        self.eolModeMac.triggered.connect(lambda: self.getTextEditWidget().changeEolMode(QsciScintilla.EolMac))
        self.eolModeMac.setData(["eolModeUnix"])
        self.eolModeMac.setCheckable(True)
        self.eolModeMenu.addAction(self.eolModeMac)

        self.editMenu.addMenu(self.eolModeMenu)
        self.editMenu.addSeparator()

        settings = QAction("&" + self.env.translate("mainWindow.menu.edit.settings"),self)
        settings.setIcon(getThemeIcon(self.env,"preferences-other"))
        settings.triggered.connect(lambda: self.env.settingsWindow.openWindow())
        settings.setData(["settings"])
        self.editMenu.addAction(settings)

        self.viewMenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.view"))

        self.zoomMenu = QMenu(self.env.translate("mainWindow.menu.view.zoom"),self)

        zoomIn = QAction(self.env.translate("mainWindow.menu.view.zoom.zoomIn"),self)
        zoomIn.triggered.connect(lambda: self.getTextEditWidget().zoomIn())
        zoomIn.setData(["zoomIn"])
        self.zoomMenu.addAction(zoomIn)

        zoomOut = QAction(self.env.translate("mainWindow.menu.view.zoom.zoomOut"),self)
        zoomOut.triggered.connect(lambda: self.getTextEditWidget().zoomOut())
        zoomOut.setData(["zoomOut"])
        self.zoomMenu.addAction(zoomOut)

        self.zoomMenu.addSeparator()

        zoom0 = QAction("0%",self)
        zoom0.triggered.connect(lambda: self.getTextEditWidget().zoomTo(-10))
        zoom0.setData(["zoom0"])
        self.zoomMenu.addAction(zoom0)

        zoom50 = QAction("50%",self)
        zoom50.triggered.connect(lambda: self.getTextEditWidget().zoomTo(-5))
        zoom50.setData(["zoom50"])
        self.zoomMenu.addAction(zoom50)

        zoom100 = QAction("100%",self)
        zoom100.triggered.connect(lambda: self.getTextEditWidget().zoomTo(0))
        zoom100.setData(["zoom100"])
        self.zoomMenu.addAction(zoom100)

        zoom150 = QAction("150%",self)
        zoom150.triggered.connect(lambda: self.getTextEditWidget().zoomTo(5))
        zoom150.setData(["zoom150"])
        self.zoomMenu.addAction(zoom150)

        zoom200 = QAction("200%",self)
        zoom200.triggered.connect(lambda: self.getTextEditWidget().zoomTo(10))
        zoom200.setData(["zoom200"])
        self.zoomMenu.addAction(zoom200)

        zoom250 = QAction("250%",self)
        zoom250.triggered.connect(lambda: self.getTextEditWidget().zoomTo(15))
        zoom250.setData(["zoom250"])
        self.zoomMenu.addAction(zoom250)

        zoom300 = QAction("300%",self)
        zoom300.triggered.connect(lambda: self.getTextEditWidget().zoomTo(20))
        zoom300.setData(["zoom300"])
        self.zoomMenu.addAction(zoom300)

        self.zoomMenu.addSeparator()

        zoomDefault = QAction(self.env.translate("mainWindow.menu.view.zoom.zoomDefault"),self)
        zoomDefault.triggered.connect(lambda: self.getTextEditWidget().zoomTo(self.env.settings.defaultZoom))
        zoomDefault.setData(["zoomDefault"])
        self.zoomMenu.addAction(zoomDefault)

        self.viewMenu.addMenu(self.zoomMenu)

        self.fullscreenAction = QAction(self.env.translate("mainWindow.menu.view.fullscreen"),self)
        self.fullscreenAction.triggered.connect(self.fullscreenMenuBarClicked)
        self.fullscreenAction.setData(["fullscreen"])
        self.fullscreenAction.setCheckable(True)
        self.viewMenu.addAction(self.fullscreenAction)

        self.toggleSidebarAction = QAction(self.env.translate("mainWindow.menu.view.sidebar"),self)
        self.toggleSidebarAction.triggered.connect(self.toggleSidebarClicked)
        self.toggleSidebarAction.setData(["toggleSidebar"])
        self.toggleSidebarAction.setCheckable(True)
        self.viewMenu.addAction(self.toggleSidebarAction)

        self.viewMenu.addSeparator()

        foldAllAction = QAction(self.env.translate("mainWindow.menu.view.foldAll"),self)
        foldAllAction.triggered.connect(lambda: self.getTextEditWidget().SendScintilla(QsciScintillaBase.SCI_FOLDALL,0))
        foldAllAction.setData(["foldAll"])
        self.viewMenu.addAction(foldAllAction)

        unfoldAllAction = QAction(self.env.translate("mainWindow.menu.view.unfoldAll"),self)
        unfoldAllAction.triggered.connect(lambda: self.getTextEditWidget().SendScintilla(QsciScintillaBase.SCI_FOLDALL,1))
        unfoldAllAction.setData(["unfoldAll"])
        self.viewMenu.addAction(unfoldAllAction)

        self.searchmenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.search"))

        search = QAction("&" + self.env.translate("mainWindow.menu.search.search"),self)
        search.setIcon(getThemeIcon(self.env,"edit-find"))
        search.triggered.connect(lambda: self.tabWidget.currentWidget().showSearchBar())
        search.setData(["find"])
        self.searchmenu.addAction(search)

        advancedSearch = QAction(self.env.translate("mainWindow.menu.search.advancedSearch"),self)
        advancedSearch.setIcon(getThemeIcon(self.env,"edit-find"))
        advancedSearch.triggered.connect(lambda: self.env.searchWindow.openWindow(self.getTextEditWidget()))
        self.searchmenu.addAction(advancedSearch)

        searchAndReplace = QAction("&" + self.env.translate("mainWindow.menu.search.searchAndReplace"),self)
        searchAndReplace.setIcon(getThemeIcon(self.env,"edit-find-replace"))
        searchAndReplace.triggered.connect(self.searchAndReplaceMenuBarClicked)
        searchAndReplace.setData(["findReplaceWindow"])
        self.searchmenu.addAction(searchAndReplace)

        gotoLine = QAction(self.env.translate("mainWindow.menu.search.gotoLine"),self)
        gotoLine.triggered.connect(lambda: self.env.gotoLineWindow.openWindow(self.getTextEditWidget()))
        gotoLine.setData(["gotoLine"])
        self.searchmenu.addAction(gotoLine)

        self.toolsMenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.tools"))

        pickColor = QAction(self.env.translate("mainWindow.menu.tools.pickColor"),self)
        pickColor.triggered.connect(self.pickColorClicked)
        pickColor.setData(["pickColor"])
        self.toolsMenu.addAction(pickColor)

        documentStatistics = QAction("&" + self.env.translate("mainWindow.menu.tools.documentStatistics"),self)
        documentStatistics.triggered.connect(lambda: self.env.documentStatistics.openWindow(self.getTextEditWidget()))
        documentStatistics.setData(["documentStatistics"])
        self.toolsMenu.addAction(documentStatistics)

        insertDateTime = QAction("&" + self.env.translate("mainWindow.menu.tools.insertDateTime"),self)
        insertDateTime.triggered.connect(lambda: self.env.dateTimeWindow.openWindow(self.getTextEditWidget()))
        insertDateTime.setData(["insertDateTime"])
        self.toolsMenu.addAction(insertDateTime)

        self.toolsMenu.addSeparator()

        stripSpacesAction = QAction(self.env.translate("mainWindow.menu.tools.stripSpaces"),self)
        stripSpacesAction.triggered.connect(self.stripSpaces)
        stripSpacesAction.setData(["stripSpaces"])
        self.toolsMenu.addAction(stripSpacesAction)

        replaceTabSpacesAction = QAction(self.env.translate("mainWindow.menu.tools.replaceTabSpaces"),self)
        replaceTabSpacesAction.triggered.connect(self.replaceTabSpaces)
        replaceTabSpacesAction.setData(["replaceTabSpaces"])
        self.toolsMenu.addAction(replaceTabSpacesAction)

        replaceSpacesTabAction = QAction(self.env.translate("mainWindow.menu.tools.replaceSpacesTab"),self)
        replaceSpacesTabAction.triggered.connect(self.replaceSpacesTab)
        replaceSpacesTabAction.setData(["replaceSpacesTab"])
        self.toolsMenu.addAction(replaceSpacesTabAction)

        self.languageMenu = self.menubar.addMenu("&" + self.env.translate("mainWindow.menu.language"))

        #self.updateLanguageMenu()

        self.encodingMenu = self.menubar.addMenu(self.env.translate("mainWindow.menu.encoding"))
        self.updateEncodingMenu()

        self.bookmarkMenu = self.menubar.addMenu(self.env.translate("mainWindow.menu.bookmarks"))

        addRemoveBookmarkAction = QAction(self.env.translate("mainWindow.menu.bookmarks.addRemoveBookmark"),self)
        addRemoveBookmarkAction.triggered.connect(self.addRemoveBookmark)
        addRemoveBookmarkAction.setData(["addRemoveBookmark"])
        self.bookmarkMenu.addAction(addRemoveBookmarkAction)

        nextBookmarkAction = QAction(self.env.translate("mainWindow.menu.bookmarks.nextBookmark"),self)
        nextBookmarkAction.triggered.connect(self.nextBookmark)
        nextBookmarkAction.setData(["nextBookmark"])
        self.bookmarkMenu.addAction(nextBookmarkAction)

        previousBookmarkAction = QAction(self.env.translate("mainWindow.menu.bookmarks.previousBookmark"),self)
        previousBookmarkAction.triggered.connect(self.previousBookmark)
        previousBookmarkAction.setData(["previousBookmark"])
        self.bookmarkMenu.addAction(previousBookmarkAction)

        clearBookmarksAction = QAction(self.env.translate("mainWindow.menu.bookmarks.clearBookmarks"),self)
        clearBookmarksAction.triggered.connect(self.clearBookmarks)
        clearBookmarksAction.setData(["clearBookmarks"])
        self.bookmarkMenu.addAction(clearBookmarksAction)

        self.macroMenu = self.menubar.addMenu(self.env.translate("mainWindow.menu.macro"))

        self.recordMacroAction = QAction(self.env.translate("mainWindow.menu.macro.startRecording"),self)
        self.recordMacroAction.triggered.connect(self.startMacroRecording)
        self.recordMacroAction.setData(["recordMacro"])

        self.stopMacroAction = QAction(self.env.translate("mainWindow.menu.macro.stopRecording"),self)
        self.stopMacroAction.triggered.connect(self.stopMacroRecording)
        self.stopMacroAction.setData(["stopMacro"])
        self.stopMacroAction.setEnabled(False)

        self.playMacroAction = QAction(self.env.translate("mainWindow.menu.macro.playMacro"),self)
        self.playMacroAction.triggered.connect(self.playMacro)
        self.playMacroAction.setData(["playMacro"])
        self.playMacroAction.setEnabled(False)

        self.saveMacroAction = QAction(self.env.translate("mainWindow.menu.macro.saveMacro"),self)
        self.saveMacroAction.triggered.connect(self.saveMacro)
        self.saveMacroAction.setData(["saveMacro"])
        self.saveMacroAction.setEnabled(False)

        self.manageMacrosAction = QAction(self.env.translate("mainWindow.menu.macro.manageMacros"),self)
        self.manageMacrosAction.triggered.connect(lambda: self.env.manageMacrosWindow.openWindow())
        self.manageMacrosAction.setData(["manageMacros"])

        self.updateMacroMenu()

        self.executeMenu = self.menubar.addMenu(self.env.translate("mainWindow.menu.execute"))

        self.executeCommandAction = QAction(self.env.translate("mainWindow.menu.execute.executeCommand"),self)
        self.executeCommandAction.triggered.connect(lambda: self.env.executeCommandWindow.openWindow(self.getTextEditWidget()))
        self.executeCommandAction.setData(["executeCommand"])

        self.editCommandsAction = QAction(self.env.translate("mainWindow.menu.execute.editCommands"),self)
        self.editCommandsAction.triggered.connect(lambda: self.env.editCommandsWindow.openWindow())
        self.editCommandsAction.setData(["editCommands"])

        self.updateExecuteMenu()

        self.aboutMenu = self.menubar.addMenu("&?")

        openDataFolder = QAction(self.env.translate("mainWindow.menu.about.openDataDir"),self)
        openDataFolder.triggered.connect(lambda: openFileDefault(self.env.dataDir))
        openDataFolder.setData(["openDataFolder"])
        self.aboutMenu.addAction(openDataFolder)

        openProgramFolder = QAction(self.env.translate("mainWindow.menu.about.openProgramDir"),self)
        openProgramFolder.triggered.connect(lambda: openFileDefault(self.env.programDir))
        openProgramFolder.setData(["openProgramFolder"])
        self.aboutMenu.addAction(openProgramFolder)

        if self.env.enableUpdater:
            searchForUpdatesAction = QAction(self.env.translate("mainWindow.menu.about.searchForUpdates"),self)
            searchForUpdatesAction.triggered.connect(lambda: searchForUpdates(self.env,False))
            searchForUpdatesAction.setData(["searchForUpdates"])
            self.aboutMenu.addAction(searchForUpdatesAction)

        showDayTip = QAction(self.env.translate("mainWindow.menu.about.dayTip"),self)
        showDayTip.triggered.connect(lambda: self.env.dayTipWindow.openWindow())
        showDayTip.setData(["showDayTip"])
        self.aboutMenu.addAction(showDayTip)

        reportBugAction = QAction(self.env.translate("mainWindow.menu.about.reportBug"),self)
        reportBugAction.triggered.connect(lambda: webbrowser.open("https://gitlab.com/JakobDev/jdTextEdit/issues/new"))
        reportBugAction.setData(["reportBug"])
        self.aboutMenu.addAction(reportBugAction)

        viewDocumentationAction = QAction(self.env.translate("mainWindow.menu.about.viewDocumentation"),self)
        viewDocumentationAction.triggered.connect(lambda: webbrowser.open("https://jdtextedit.readthedocs.io"))
        viewDocumentationAction.setData(["viewDocumentation"])
        self.aboutMenu.addAction(viewDocumentationAction)

        self.aboutMenu.addSeparator()

        about = QAction(self.env.translate("mainWindow.menu.about.about"),self)
        about.triggered.connect(lambda: self.env.aboutWindow.show())
        about.setData(["about"])
        self.aboutMenu.addAction(about)

        aboutQt = QAction(self.env.translate("mainWindow.menu.about.aboutQt"),self)
        aboutQt.triggered.connect(QApplication.instance().aboutQt)
        aboutQt.setData(["aboutQt"])
        self.aboutMenu.addAction(aboutQt)

        self.updateRecentFilesMenu()
        #self.getMenuActions(self.menubar)
        separator = QAction(self.env.translate("mainWindow.separator"))
        separator.setData(["separator"])
        self.env.menuActions["separator"] = separator

    def updateToolbar(self, settings):
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
            #lexer = action.data().getLexer()
            #self.getTextEditWidget().setSyntaxHighlighter(lexer,lexerList=action.data())
            self.getTextEditWidget().setLanguage(action.data())

    def languagePlainTextClicked(self):
        editWidget = self.getTextEditWidget()
        #editWidget.setLexer(None)
        #editWidget.currentLexer = None
        #editWidget.updateSettings(self.env.settings)
        #editWidget.lexerName = self.env.translate("mainWindow.menu.language.plainText")
        #editWidget.updateStatusBar()
        #editWidget.removeSyntaxHighlighter()
        editWidget.removeLanguage()

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
        if hasattr(self,"tabWidget"):
           self.updateSelectedLanguage()

    def updateSelectedLanguage(self):
        if not hasattr(self.env,"languageActionList"):
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
        isoMenu = QMenu("ISO",self)
        utfMenu = QMenu("UTF",self)
        windowsMenu = QMenu("windows",self)
        self.encodingMenu.addMenu(isoMenu)
        self.encodingMenu.addMenu(utfMenu)
        self.encodingMenu.addMenu(windowsMenu)
        for i in getEncodingList():
            encodingAction = QAction(i[0],self)
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
            command.triggered.connect(lambda sender: executeCommand(self.sender().data()[1],self.getTextEditWidget(),self.sender().data()[2]))
            self.executeMenu.addAction(command)

        for i in self.env.global_commands:
            command = QAction(i[0],self)
            command.setData([False,i[1],i[2]])
            command.triggered.connect(lambda sender: executeCommand(self.sender().data()[1],self.getTextEditWidget(),self.sender().data()[2]))
            self.executeMenu.addAction(command)

        self.executeMenu.addSeparator()

        self.executeMenu.addAction(self.editCommandsAction)

    def openFile(self, path: str, template=None, reload=None):
        #Check if the file is already open
        if not template:
            for i in range(self.tabWidget.count()):
                if self.tabWidget.widget(i).getCodeEditWidget().getFilePath() == path:
                    self.tabWidget.setCurrentIndex(i)
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
        fileContent = fileBytes.decode(encoding,errors="replace")
        filehandle.close()
        if (not self.getTextEditWidget().isNew) and (not reload):
            self.tabWidget.createTab(self.env.translate("mainWindow.newTabTitle"),focus=True)
        containerWidget = self.tabWidget.currentWidget()
        editWidget = containerWidget.getCodeEditWidget()
        if isBigFile and self.env.settings.bigFileDisableHighlight:
            editWidget.removeLanguage()
        editWidget.bigFile = isBigFile
        editWidget.setText(fileContent)
        editWidget.setModified(False)
        self.tabWidget.tabsChanged.emit()
        if not template:
            editWidget.setFilePath(path)
            self.tabWidget.setTabText(self.tabWidget.currentIndex(),os.path.basename(path))
        self.updateWindowTitle()
        if self.env.settings.detectEol:
            lines = fileContent.splitlines(True)
            if len(lines) != 0:
                firstLine = lines[0]
                if firstLine.endswith("\r\n"):
                    editWidget.setEolMode(QsciScintilla.EolWindows)
                elif firstLine.endswith("\n"):
                    editWidget.setEolMode(QsciScintilla.EolUnix)
                elif firstLine.endswith("\r"):
                    editWidget.setEolMode(QsciScintilla.EolMac)
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
                        languageFound= True
                        break
                if languageFound:
                    break
        containerWidget.clearBanner()
        if self.env.settings.useEditorConfig:
            editWidget.loadEditorConfig()
        if editWidget.settings.defaultEncoding != encoding and self.env.settings.showEncodingBanner:
            containerWidget.showBanner(WrongEncodingBanner(self.env,containerWidget))
        if self.env.settings.showEolBanner:
            if editWidget.eolMode() == QsciScintilla.EolWindows and editWidget.settings.defaultEolMode != 0:
                containerWidget.showBanner(WrongEolBanner(self.env,containerWidget))
            elif editWidget.eolMode() == QsciScintilla.EolUnix and editWidget.settings.defaultEolMode != 1:
                containerWidget.showBanner(WrongEolBanner(self.env,containerWidget))
            elif editWidget.eolMode() == QsciScintilla.EolMac and editWidget.settings.defaultEolMode != 2:
                containerWidget.showBanner(WrongEolBanner(self.env,containerWidget))
        if isBigFile and self.env.settings.bigFileShowBanner:
            containerWidget.showBanner(BigFileBanner(self.env,containerWidget))
        self.env.editorSignals.openFile.emit(editWidget)

    def saveFile(self, tabid):
        containerWidget = self.tabWidget.widget(tabid)
        editWidget = containerWidget.getCodeEditWidget()
        path = editWidget.getFilePath()
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
            filehandle = open(path,"wb")
        except PermissionError:
            showMessageBox(self.env.translate("noWritePermission.title"),self.env.translate("noWritePermission.text") % editWidget.getFilePath())
            return
        except Exception as e:
            print(e)
            showMessageBox(self.env.translate("unknownError.title"),self.env.translate("unknownError.text"))
            return
        filehandle.write(text)
        filehandle.close()
        containerWidget.fileWatcher.addPath(path)
        editWidget.setModified(False)
        self.updateWindowTitle()
        if self.env.settings.detectLanguage:
            for i in self.env.lexerList:
                for e in i["extension"]:
                    if path.endswith(e):
                        lexer = i["lexer"]()
                        editWidget.setSyntaxHighlighter(lexer,lexerList=i)

    def newMenuBarClicked(self):
        self.tabWidget.createTab(self.env.translate("mainWindow.newTabTitle"),focus=True)

    def openMenuBarClicked(self):
        #fileDialog = QFileDialog(self)
        #fileDialog.set
        path = QFileDialog.getOpenFileName(self,self.env.translate("mainWindow.openFileDialog.title"),None,self.env.fileNameFilters)
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
        if self.getTextEditWidget().getFilePath() == "":
            self.saveAsMenuBarClicked(tabid)
        else:
            self.saveFile(tabid)

    def deleteMenuBarClicked(self):
        lastText = self.env.clipboard.text()
        self.getTextEditWidget().cut()
        self.env.clipboard.setText(lastText)

    def saveAsMenuBarClicked(self,tabid):
        path = QFileDialog.getSaveFileName(self,self.env.translate("mainWindow.saveAsDialog.title"),None,self.env.fileNameFilters)

        if path[0]:
            self.getTextEditWidget().setFilePath(path[0])
            self.saveFile(tabid)
            self.tabWidget.setTabText(tabid,os.path.basename(path[0]))
            self.tabWidget.tabsChanged.emit()
            self.updateWindowTitle()

    def saveAllMenuBarClicked(self):
        for i in range(self.tabWidget.count()):
            self.saveMenuBarClicked(i)

    def closeAllTabs(self):
        for i in range(self.tabWidget.count()-1,-1,-1):
            self.tabWidget.tabCloseClicked(i,notCloseProgram=True)
        self.tabWidget.createTab(self.env.translate("mainWindow.newTabTitle"),focus=True)

    def printMenuBarClicked(self):
        dialog  = QPrintDialog(printer);
        dialog.setWindowTitle(self.env.translate("mainWindow.printDialog.title"));
        if dialog.exec() == QDialog.Accepted:
            editWidget = self.getTextEditWidget()
            printer.printRange(editWidget)

    def fullscreenMenuBarClicked(self):
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
        #editWidget.setCursorPosition(editWidget.bookmarkList[-1],0)

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

    def autoSaveTimeout(self):
        if self.autoSaveTimer.timeout == 0 or not self.env.settings.enableAutoSave:
            return
        for i in range(self.tabWidget.count()):
            if self.tabWidget.widget(i).getCodeEditWidget().getFilePath() != "":
                self.saveFile(i)

    def updateSettings(self, settings):
        self.env.recentFiles = self.env.recentFiles[:self.env.settings.maxRecentFiles]
        self.updateRecentFilesMenu()
        self.updateToolbar(settings)
        self.setToolButtonStyle(settings.toolbarIconStyle)
        if settings.showToolbar:
            self.toolbar.show()
        else:
            self.toolbar.close()
        toolbarPositionList = [Qt.TopToolBarArea,Qt.BottomToolBarArea,Qt.LeftToolBarArea,Qt.RightToolBarArea]
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
        self.tabWidget.updateSettings(settings)
        self.updateWindowTitle()

    def updateWindowTitle(self):
        if self.env.settings.windowFileTitle:
            self.setWindowTitle(self.tabWidget.tabText(self.tabWidget.currentIndex()) + " - jdTextEdit")
        else:
            self.setWindowTitle("jdTextEdit")

    def restoreSession(self):
        with open(os.path.join(self.env.dataDir,"session.json"),"r",encoding="utf-8") as f:
            data = json.load(f)
        for count, i in enumerate(data["tabs"]):
            if i["path"] == "":
                self.tabWidget.createTab(self.env.translate("mainWindow.newTabTitle"))
            else:
                self.tabWidget.createTab(os.path.basename(i["path"]))
            editWidget = self.tabWidget.widget(count).getCodeEditWidget()
            f = open(os.path.join(self.env.dataDir,"session_data",str(count)),"rb")
            text = f.read().decode(i["encoding"],errors="replace")
            editWidget.setText(text)
            f.close()
            editWidget.restoreSaveMetaData(i)
        self.tabWidget.setCurrentIndex(data["selectedTab"])
        if "currentMacro" in data:
            self.currentMacro = QsciMacro(self.getTextEditWidget())
            self.currentMacro.load(data["currentMacro"])
            self.playMacroAction.setEnabled(True)
            self.saveMacroAction.setEnabled(True)
        self.updateSelectedLanguage()
        os.remove(os.path.join(self.env.dataDir,"session.json"))
        shutil.rmtree(os.path.join(self.env.dataDir,"session_data"))

    def saveDataClose(self):
        self.env.settings.showSidepane = self.env.sidepane.enabled
        self.env.settings.sidepaneWidget = self.env.sidepane.content.getSelectedWidget()
        self.env.settings.save(os.path.join(self.env.dataDir,"settings.json"))
        if self.env.settings.saveWindowState:
            windowState = {}
            saveWindowState(self,windowState,"MainWindow")
            saveWindowState(self.env.settingsWindow,windowState,"SettingsWindow")
            saveWindowState(self.env.dayTipWindow,windowState,"DayTipWindow")
            saveWindowState(self.env.editCommandsWindow,windowState,"EditCommandsWindow")
            saveWindowState(self.env.dateTimeWindow,windowState,"DateTimeWindow")
            saveWindowState(self.env.manageMacrosWindow,windowState,"ManageMacrosWindow")
            with open(os.path.join(self.env.dataDir,"windowstate.json"), 'w', encoding='utf-8') as f:
                json.dump(windowState, f, ensure_ascii=False, indent=4)
        else:
            try:
                os.remove(os.path.join(self.env.dataDir,"windowstate.json"))
            except:
                pass

    def closeEvent(self, event):
        self.saveDataClose()
        if self.env.settings.saveSession:
            if not os.path.isdir(os.path.join(self.env.dataDir,"session_data")):
                os.mkdir(os.path.join(self.env.dataDir,"session_data"))
            data = {}
            data["selectedTab"] = self.tabWidget.currentIndex()
            if self.currentMacro:
                data["currentMacro"] = self.currentMacro.save()
            data["tabs"] = []
            for i in range(self.tabWidget.count()):
                widget = self.tabWidget.widget(i).getCodeEditWidget()
                f = open(os.path.join(self.env.dataDir,"session_data",str(i)),"wb")
                f.write(widget.text().encode(widget.getUsedEncoding(),errors="replace"))
                f.close()
                #if widget.currentLexer:
                #    syntax = widget.currentLexer.language()
                #else:
                #    syntax = ""
                #data["tabs"].append({"path":widget.getFilePath(),"modified":widget.isModified(),"language":syntax,"encoding":widget.getUsedEncoding(),"bookmarks":widget.bookmarkList,"cursorPosLine":widget.cursorPosLine,"cursorPosIndex":widget.cursorPosIndex})
                data["tabs"].append(widget.getSaveMetaData())
            with open(os.path.join(self.env.dataDir,"session.json"), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            sys.exit(0)
        else:
            for i in range(self.tabWidget.count()-1,-1,-1):
                self.tabWidget.tabCloseClicked(i,forceExit=True)
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
