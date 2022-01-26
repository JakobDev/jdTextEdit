from PyQt6.QtWidgets import QMenu
from PyQt6.Qsci import QsciScintilla, QsciLexer, QsciScintillaBase, QsciMacro
from PyQt6.QtGui import QColor, QFontMetrics, QFont, QCursor
from PyQt6.QtCore import pyqtSignal
from jdTextEdit.gui.BannerWidgets.EditorconfigBanner import EditorconfigBanner
from jdTextEdit.api.LanguageBase import LanguageBase
import traceback
import copy
import sys
import os


try:
    import editorconfig
except ModuleNotFoundError:
    print("editorconfig module not found", file=sys.stderr)


class CodeEdit(QsciScintilla):
    pathChanged = pyqtSignal("QString")
    def __init__(self, env, preview=None, isNew=False, container=None):
        super().__init__()
        self.env = env
        self.isPreview = preview
        self.isNew = isNew
        self.container = container
        self.currentLexer = None
        self.apiCompletion = None
        self.searchText = ""
        self.tabid = None
        self.usedEncoding = env.settings.defaultEncoding
        self.filePath = ""
        self.cursorPosLine = 0
        self.cursorPosIndex = 0
        self.bookmarkList = []
        self.settings = copy.copy(self.env.settings)
        self.custom_settings = {}
        self.language = None
        self.bigFile = False
        self.currentIdicatorNumber = 0
        self.cursorPosString = env.translate("mainWindow.statusBar.cursorPosLabel") % (1,1)
        self.languageName = env.translate("mainWindow.menu.language.plainText")
        self.foldStyles = [QsciScintilla.FoldStyle.NoFoldStyle,QsciScintilla.FoldStyle.PlainFoldStyle,QsciScintilla.FoldStyle.CircledFoldStyle,QsciScintilla.FoldStyle.BoxedFoldStyle,QsciScintilla.FoldStyle.CircledTreeFoldStyle,QsciScintilla.FoldStyle.BoxedTreeFoldStyle]
        eolModeList = [QsciScintilla.EolMode.EolWindows,QsciScintilla.EolMode.EolUnix,QsciScintilla.EolMode.EolMac]
        self.changeEolMode(eolModeList[self.settings.defaultEolMode])
        self.updateSettings(self.settings)
        self.setMarginLineNumbers(0, True)
        self.setUtf8(True)
        self.modificationChanged.connect(self.modificationStateChange)
        self.marginClicked.connect(self.marginClickCallback)
        self.setMarginSensitivity(1,True)
        #self.modificationStateChange(False)
        #self.setMarginsBackgroundColor(QColor("#cccccc"))
        #self.setWrapVisualFlags(QsciScintilla.WrapVisualFlag.WrapFlagByText)

        self.textChanged.connect(self.textEdited)
        self.selectionChanged.connect(self.editSelectionChanged)
        self.cursorPositionChanged.connect(self.updateCursor)

        self.linesChanged.connect(lambda: self.env.editorSignals.linesChanged.emit(self))
        self.textChanged.connect(lambda: self.env.editorSignals.textChanged.emit(self))
        self.indicatorClicked.connect(lambda line,index,keys: self.env.editorSignals.indicatorClicked.emit(self,line,index,keys))
        self.indicatorReleased.connect(lambda line,index,keys: self.env.editorSignals.indicatorReleased.emit(self,line,index,keys))

        if self.settings.defaultLanguage != "plain":
            for l in self.env.languageList:
                if l.getID() == self.settings.defaultLanguage:
                    self.setLanguage(l)

        self.setMarginType(1, QsciScintilla.MarginType.SymbolMargin)
        sym_4 = QsciScintilla.MarkerSymbol.Circle
        self.markerDefine(sym_4, 0)
        #self.setMarginWidth(1, 10)

        self.zoomTo(self.settings.defaultZoom)

        self.env.editorSignals.editorInit.emit(self)

    def updateStatusBar(self):
        if self.isPreview or not hasattr(self.env,"mainWindow"):
            return
        self.env.mainWindow.pathLabel.setText(self.filePath)
        self.env.mainWindow.encodingLabel.setText(self.usedEncoding)
        self.env.mainWindow.lexerLabel.setText(self.languageName)
        self.env.mainWindow.cursorPosLabel.setText(self.cursorPosString)
        if self.eolMode() == QsciScintilla.EolMode.EolWindows:
            self.env.mainWindow.eolLabel.setText("CRLF")
        elif self.eolMode() == QsciScintilla.EolMode.EolUnix:
            self.env.mainWindow.eolLabel.setText("LF")
        elif self.eolMode() == QsciScintilla.EolMode.EolMac:
            self.env.mainWindow.eolLabel.setText("CR")

    def setLanguage(self,lang: LanguageBase):
        """
        Sets the Language.
        :param lang: The Language
        """
        lexer = lang.getLexer()
        self.currentLexer = lexer
        self.setLexer(lexer)
        self.language = lang
        if not self.isPreview:
            self.languageName = lang.getName()
            self.updateStatusBar()
            if not hasattr(self.env,"mainWindow"):
                return
            self.env.mainWindow.updateSelectedLanguage()
        self.updateSettings(self.settings)
        self.env.editorSignals.languageChanged.emit(self,lang)

    def removeLanguage(self):
        """
        Sets the Language to Plain Text
        """
        self.setLexer(None)
        self.currentLexer = None
        self.language = None
        self.updateSettings(self.settings)
        self.lexerName = self.env.translate("mainWindow.menu.language.plainText")
        self.updateStatusBar()
        self.env.editorSignals.languageChanged.emit(self,None)

    def insertText(self, text: str):
        self.insert(text)
        line, pos = self.getCursorPosition()
        self.setCursorPosition(line,pos + len(text))

    def modificationStateChange(self, state):
        if self.isPreview:
            return
        tabWidget = self.container.getTabWidget()
        try:
            if state:
                tabWidget.setTabIcon(self.tabid,self.env.documentUnsavedIcon)
            else:
                tabWidget.setTabIcon(self.tabid,self.env.documentSavedIcon)
        except:
            pass

    def textEdited(self):
        if self.isPreview:
            return
        self.isNew = False
        if not hasattr(self.env, "mainWindow"):
            return
        if self.isUndoAvailable():
            self.env.mainWindow.undoMenubarItem.setEnabled(True)
        else:
            self.env.mainWindow.undoMenubarItem.setEnabled(False)
        if self.isRedoAvailable():
            self.env.mainWindow.redoMenubarItem.setEnabled(True)
        else:
            self.env.mainWindow.redoMenubarItem.setEnabled(False)

    def editSelectionChanged(self):
        if self.isPreview:
            return
        try:
            if self.hasSelectedText():
                self.env.mainWindow.cutMenubarItem.setEnabled(True)
                self.env.mainWindow.copyMenubarItem.setEnabled(True)
                self.env.mainWindow.deleteMenubarItem.setEnabled(True)
            else:
                self.env.mainWindow.cutMenubarItem.setEnabled(False)
                self.env.mainWindow.copyMenubarItem.setEnabled(False)
                self.env.mainWindow.deleteMenubarItem.setEnabled(False)
        except:
            pass

    def updateCursor(self, line, pos):
        #self.SendScintilla(QsciScintillaBase.SCI_INDICATORFILLRANGE,0,10)
        self.cursorPosLine = line
        self.cursorPosIndex = pos
        if not self.isPreview:
            self.cursorPosString = self.env.translate("mainWindow.statusBar.cursorPosLabel") % (line + 1, pos + 1)
            self.updateStatusBar()

    def marginClickCallback(self, margin, line):
        if margin == 1:
            self.addRemoveBookmark(line)

    def addRemoveBookmark(self, line):
        if line in self.bookmarkList:
            self.markerDelete(line,0)
            self.bookmarkList.remove(line)
        else:
            self.markerAdd(line, 0)
            self.bookmarkList.append(line)

    def updateEolMenu(self):
        if self.isPreview or not hasattr(self.env,"mainWindow"):
            return
        self.env.mainWindow.eolModeWindows.setChecked(False)
        self.env.mainWindow.eolModeUnix.setChecked(False)
        self.env.mainWindow.eolModeMac.setChecked(False)
        if self.eolMode() == QsciScintilla.EolMode.EolWindows:
            self.env.mainWindow.eolModeWindows.setChecked(True)
        elif self.eolMode() == QsciScintilla.EolMode.EolUnix:
            self.env.mainWindow.eolModeUnix.setChecked(True)
        elif self.eolMode() == QsciScintilla.EolMode.EolMac:
            self.env.mainWindow.eolModeMac.setChecked(True)

    def changeEolMode(self, mode):
        self.setEolMode(mode)
        self.convertEols(mode)
        self.updateEolMenu()
        self.updateStatusBar()

    def getEolChar(self):
        if self.eolMode() == QsciScintilla.EolMode.EolWindows:
            return "\r\n"
        elif self.eolMode() == QsciScintilla.EolMode.EolUnix:
            return "\n"
        elif self.eolMode() == QsciScintilla.EolMode.EolMac:
            return "\r"

    def setUsedEncoding(self, encoding):
        self.usedEncoding = encoding
        self.updateEncodingMenu()
        self.updateStatusBar()

    def getUsedEncoding(self):
        return self.usedEncoding

    def updateEncodingMenu(self):
        for i in self.env.encodingActions:
            if i.text() == self.usedEncoding:
                i.setChecked(True)
            else:
                i.setChecked(False)

    def setFilePath(self, path):
        self.filePath = path
        self.updateStatusBar()
        self.pathChanged.emit(path)

    def getFilePath(self):
        return self.filePath

    def updateMenuActions(self):
        if self.isPreview:
            return
        if self.isUndoAvailable():
            self.env.mainWindow.undoMenubarItem.setEnabled(True)
        else:
            self.env.mainWindow.undoMenubarItem.setEnabled(False)
        if self.isRedoAvailable():
            self.env.mainWindow.redoMenubarItem.setEnabled(True)
        else:
            self.env.mainWindow.redoMenubarItem.setEnabled(False)
        self.editSelectionChanged()
        self.updateEncodingMenu()
        if not hasattr(self.env,"mainWindow"):
            return
        self.env.mainWindow.updateSelectedLanguage()

    def contextMenuEvent(self, event):
        event.setAccepted(False)
        self.env.editorSignals.contextMenu.emit(self,event)
        if event.isAccepted():
            return
        event.accept()
        menu = QMenu("jdTextEdit",self)
        for i in self.settings.editContextMenu:
            if i == "separator":
                menu.addSeparator()
            else:
                if i in self.env.menuActions:
                    menu.addAction(self.env.menuActions[i])
        menu.setTearOffEnabled(True)
        menu.popup(QCursor.pos())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ingore()

    def dropEvent(self, event):
        for i in event.mimeData().urls():
            if i.url().startswith("file://"):
                self.env.mainWindow.openFile(i.url()[7:])
        if event.mimeData().text() != "" and len(event.mimeData().urls()) == 0:
            self.insertText(event.mimeData().text())

    def getSaveMetaData(self):
        if self.language:
            syntax = self.language.getID()
        else:
            syntax = ""
        path = self.getFilePath()
        if path == "":
            modificationTime = 0
        else:
            try:
                modificationTime = os.path.getmtime(path)
            except:
                modificationTime = 0
        fileChangedBannerVisible = self.container.isFileChangedBannerVisible()
        data = {
            "path": path,
            "modified": self.isModified(),
            "language": syntax,
            "encoding": self.getUsedEncoding(),
            "bookmarks": self.bookmarkList,
            "cursorPosLine": self.cursorPosLine,
            "cursorPosIndex": self.cursorPosIndex,
            "zoom": self.getZoom(),
            "customSettings": self.custom_settings,
            "overwriteMode": self.overwriteMode(),
            "fileChangedBannerVisible": fileChangedBannerVisible,
            "modificationTime": modificationTime
        }
        self.env.editorSignals.saveSession.emit(self,data)
        return data

    def restoreSaveMetaData(self,data):
        path = data.get("path","")
        self.setFilePath(path)
        self.setModified(data["modified"])
        self.setUsedEncoding(data.get("encoding",self.settings.defaultEncoding))
        syntax = data.get("language", "")
        if syntax != "":
            for l in self.env.languageList:
                if  l.getID() == syntax:
                    self.setLanguage(l)
        self.bookmarkList = data.get("bookmarks",[])
        for line in self.bookmarkList:
            self.markerAdd(line, 0)
        self.setCursorPosition(data["cursorPosLine"],data["cursorPosIndex"])
        self.zoomTo(data.get("zoom",self.settings.defaultZoom))
        self.custom_settings = data.get("customSettings",{})
        self.settings.loadDict(self.custom_settings)
        if len(self.custom_settings) != 0:
            self.updateSettings(self.settings)
        self.setOverwriteMode(data.get("overwriteMode",False))
        modificationTime = data.get("modificationTime",0)
        if self.container:
            if not os.path.exists(path) and path != "":
                self.container.showFileDeletedBanner()
            elif data.get("fileChangedBannerVisible",False):
                self.container.showFileChangedBanner()
            elif modificationTime != 0:
                if modificationTime != os.path.getmtime(path):
                    self.container.showFileChangedBanner()
        self.env.editorSignals.restoreSession.emit(self,data)

    def loadEditorConfig(self):
        """
        Loads a .editorconfig file
        """
        try:
            config = editorconfig.get_properties(self.getFilePath())
        except NameError:
            print("Trying to load a file with editorconfig enabled while the editorconfig module is not installed", file=sys.stderr)
            return
        except Exception:
            print("Error occurred while getting .editorconfig properties", file=sys.stderr)
            return
        if "indent_style" in config and self.settings.editorConfigUseIndentStyle:
            if config["indent_style"] == "space":
                self.custom_settings["editTabSpaces"] = True
            elif config["indent_style"] == "tab":
                self.custom_settings["editTabSpaces"] = False
        if self.settings.editorConfigTabWidth:
            try:
                self.custom_settings["editTabWidth"] = int(config["indent_size"])
            except:
                pass
        if "tab_width" in config and self.settings.editorConfigTabWidth:
            self.custom_settings["editTabWidth"] = int(config["tab_width"])
        if "end_of_line" in config and self.settings.editorConfigEndOfLine:
            if config["end_of_line"] == "crlf":
                self.custom_settings["defaultEolMode"] = 0
            elif config["end_of_line"] == "lf":
                self.custom_settings["defaultEolMode"] = 1
            elif config["end_of_line"] == "cr":
                self.custom_settings["defaultEolMode"] = 2
        if "trim_trailing_whitespace" in config and self.settings.editorConfigTrimWhitespace:
            if config["trim_trailing_whitespace"] == "true":
                self.custom_settings["stripSpacesSave"] = True
            elif config["trim_trailing_whitespace"] == "false":
                self.custom_settings["stripSpacesSave"] = False
        if "insert_final_newline" in config and self.settings.editorConfigInsertNewline:
            if config["insert_final_newline"] == "true":
                self.custom_settings["eolFileEnd"] = True
            elif config["insert_final_newline"] == "false":
                self.custom_settings["eolFileEnd"] = False
        self.settings.loadDict(self.custom_settings)
        self.updateSettings(self.settings)
        if self.container and self.settings.editorConfigShowBanner:
            self.container.showBanner(EditorconfigBanner(self.env,self.container))

    def changeFont(self,font,settings):
        self.setFont(font)
        self.setMarginsFont(font)
        fontmetrics = QFontMetrics(font)
        if settings.editShowLineNumbers:
            self.setMarginWidth(0, fontmetrics.averageCharWidth() * 6)
        else:
            self.setMarginWidth(0,0)
        if self.currentLexer:
            self.currentLexer.setFont(font)
            self.currentLexer.setDefaultFont(font)

    def setSettings(self, settings):
        settings = copy.copy(settings)
        settings.loadDict(self.custom_settings)
        self.updateSettings(settings)
        self.env.editorSignals.settingsChanged.emit(self,settings)

    def updateSettings(self, settings):
        if settings.editTheme in self.env.themes:
            try:
                self.env.themes[settings.editTheme].applyTheme(self,self.currentLexer)
            except Exception as e:
                print(traceback.format_exc(), end="", file=sys.stderr)
                self.env.themes["builtin.default"].applyTheme(self, self.currentLexer)
        else:
            print("The selected Theme could not be found. Falling back to the default Theme.",file=sys.stderr)
            self.env.themes["builtin.default"].applyTheme(self,self.currentLexer)
        if settings.useCustomFont:
            self.changeFont(settings.editFont,settings)
        else:
            self.changeFont(QFont(),settings)
        self.setFolding(self.foldStyles[settings.editFoldStyle])
        self.setCaretLineVisible(settings.highlightCurrentLine)
        self.setTabWidth(settings.editTabWidth)
        self.setIndentationsUseTabs(not settings.editTabSpaces)
        if settings.get("editTextWrap"):
            self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        else:
            self.setWrapMode(QsciScintilla.WrapMode.WrapNone)
        if settings.get("editShowWhitespaces"):
            self.setWhitespaceVisibility(QsciScintilla.WhitespaceVisibility.WsVisible)
        else:
            self.setWhitespaceVisibility(QsciScintilla.WhitespaceVisibility.WsInvisible)
        self.setAutoIndent(settings.editAutoIndent)
        self.setEolVisibility(settings.editShowEol)
        self.setIndentationGuides(settings.showIndentationGuides)
        if settings.enableAutocompletion:
            if settings.autocompletionUseDocument and settings.autocompletionUseAPI:
                self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
            elif settings.autocompletionUseDocument:
                self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsDocument)
            elif settings.autocompletionUseAPI:
                self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAPIs)
            else:
                self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsNone)
            self.setAutoCompletionCaseSensitivity(settings.autocompletionCaseSensitive)
            self.setAutoCompletionThreshold(settings.autocompleteThreshold)
            self.setAutoCompletionReplaceWord(settings.autocompletionReplaceWord)
            if self.currentLexer and settings.autocompletionUseAPI and self.language:
                api = self.language.getAPI(self.currentLexer)
                #if api:
                    #com
                #if isinstance(self.apiCompletion, str):
                    #api = AutocompleteXML(self.currentLexer,self.apiCompletion)
                #else:
                    #api = self.apiCompletion(self.currentLexer)
        else:
            self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsNone)
        self.settings = settings

    def positionFromPoint(self,point):
        return self.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINTCLOSE,point.x(), point.y())

    def isBigFile(self):
        return self.bigFile

    def getIndicatorNumber(self):
        self.currentIdicatorNumber += 1
        return self.currentIdicatorNumber - 1

    def getLanguage(self):
        return self.language

    def getZoom(self) -> int:
        """
        Returns the current zoom
        :return: zoom
        """
        return self.SendScintilla(QsciScintillaBase.SCI_GETZOOM)

    def updateOtherWidgets(self):
        """
        Updates the other widgets like MainWindow or the statusbar
        :return:
        """
        self.updateEolMenu()
        self.updateStatusBar()
        self.updateMenuActions()
        self.env.mainWindow.updateWindowTitle()
        if self.env.mainWindow.currentMacro:
            self.env.mainWindow.stopMacroRecording()
            macro = self.env.mainWindow.currentMacro.save()
            self.env.mainWindow.currentMacro = QsciMacro(self)
            self.env.mainWindow.currentMacro.load(macro)

    def focusInEvent(self, event):
        if self.isPreview:
            return
        self.container.getTabWidget().markWidgetAsActive()
        self.updateOtherWidgets()
        super().focusInEvent(event)
