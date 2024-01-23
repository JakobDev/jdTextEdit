from PyQt6.QtWidgets import QMenu
from PyQt6.Qsci import QsciScintilla, QsciScintillaBase, QsciMacro, QsciLexer
from PyQt6.QtGui import QFontMetrics, QFont, QCursor, QContextMenuEvent, QDragEnterEvent, QDropEvent, QFocusEvent
from PyQt6.QtCore import QPoint, QCoreApplication, pyqtSignal
from jdTextEdit.gui.BannerWidgets.EditorconfigBanner import EditorconfigBanner
from jdTextEdit.api.LanguageBase import LanguageBase
from typing import Optional, Any, TYPE_CHECKING
from jdTextEdit.Functions import findAllText
import copy
import sys
import os


try:
    import editorconfig
except ModuleNotFoundError:
    print("editorconfig module not found", file=sys.stderr)


if TYPE_CHECKING:
    from jdTextEdit.gui.EditContainer import EditContainer
    from jdTextEdit.gui.MainWindow import MainWindow
    from jdTextEdit.api.ThemeBase import ThemeBase
    from jdTextEdit.Environment import Environment
    from jdTextEdit.Settings import Settings


class CodeEdit(QsciScintilla):
    pathChanged = pyqtSignal("QString")

    def __init__(self, env: "Environment", preview: bool = False, isNew: bool = False, container: Optional["EditContainer"] = None) -> None:
        super().__init__()
        self.env = env
        self.isPreview = preview
        self.isNew = isNew
        self.container = container
        self.currentLexer: Optional[QsciLexer] = None
        self.apiCompletion = None
        self.searchText = ""
        self.tabid: Optional[int] = None
        self.usedEncoding = env.settings.get("defaultEncoding")
        self.filePath = ""
        self.cursorPosLine = 0
        self.cursorPosIndex = 0
        self.bookmarkList: list[int] = []
        self.settings = copy.copy(self.env.settings)
        self.custom_settings = {}
        self.language = None
        self.bigFile = False
        self.customTabName = ""
        self.currentIndicatorNumber = 0
        self._customTheme = None
        self.languageName = QCoreApplication.translate("CodeEdit", "Plain Text")
        self.foldStyles = [QsciScintilla.FoldStyle.NoFoldStyle, QsciScintilla.FoldStyle.PlainFoldStyle, QsciScintilla.FoldStyle.CircledFoldStyle, QsciScintilla.FoldStyle.BoxedFoldStyle, QsciScintilla.FoldStyle.CircledTreeFoldStyle, QsciScintilla.FoldStyle.BoxedTreeFoldStyle]

        if container is not None:
            self._mainWindow: Optional["MainWindow"] = container.getTabWidget().getSplitViewWidget().getMainWindow()
        else:
            self._mainWindow: Optional["MainWindow"] = None

        eolModeList = [QsciScintilla.EolMode.EolWindows, QsciScintilla.EolMode.EolUnix, QsciScintilla.EolMode.EolMac]
        self.changeEolMode(eolModeList[self.settings.defaultEolMode])

        # Highlight all Ocuurences of selcted text
        self._highlightOccurrencesIndicator = self.getIndicatorNumber()
        self.indicatorDefine(QsciScintilla.IndicatorStyle.FullBoxIndicator, self._highlightOccurrencesIndicator)
        self.selectionChanged.connect(self._updateHighlightAllOccurrences)

        self.updateSettings(self.settings)

        self.setMarginLineNumbers(0, True)
        self.setUtf8(True)
        self.modificationChanged.connect(self.modificationStateChange)
        self.marginClicked.connect(self.marginClickCallback)
        self.setMarginSensitivity(1, True)
        #self.modificationStateChange(False)
        #self.setMarginsBackgroundColor(QColor("#cccccc"))
        #self.setWrapVisualFlags(QsciScintilla.WrapVisualFlag.WrapFlagByText)

        self.textChanged.connect(self.textEdited)
        self.selectionChanged.connect(self.editSelectionChanged)
        self.cursorPositionChanged.connect(self.updateCursor)

        self.linesChanged.connect(lambda: self.env.editorSignals.linesChanged.emit(self))
        self.textChanged.connect(lambda: self.env.editorSignals.textChanged.emit(self))
        self.indicatorClicked.connect(lambda line, index, keys: self.env.editorSignals.indicatorClicked.emit(self, line, index, keys))
        self.indicatorReleased.connect(lambda line, index, keys: self.env.editorSignals.indicatorReleased.emit(self, line, index, keys))

        if self.settings.defaultLanguage != "plain":
            lang = env.getLanguageByID(self.settings.get("defaultLanguage"))
            if lang is not None:
                self.setLanguage(lang)

        self.setMarginType(1, QsciScintilla.MarginType.SymbolMargin)
        sym_4 = QsciScintilla.MarkerSymbol.Circle
        self.markerDefine(sym_4, 0)
        #self.setMarginWidth(1, 10)

        self.zoomTo(self.settings.get("defaultZoom"))

        self.env.editorSignals.editorInit.emit(self)

    def updateStatusBar(self):
        if self.isPreview or self._mainWindow is None:
            return
        self._mainWindow.updateStatusBar()

    def setLanguage(self, lang: LanguageBase):
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
            if self._mainWindow is not None:
                self._mainWindow.updateSelectedLanguage()
        self.updateSettings(self.settings)
        self.env.editorSignals.languageChanged.emit(self, lang)

    def removeLanguage(self):
        """
        Sets the Language to Plain Text
        """
        self.setLexer(None)
        self.currentLexer = None
        self.language = None
        self.updateSettings(self.settings)
        self.lexerName = QCoreApplication.translate("CodeEdit", "Plain Text")
        self.updateStatusBar()
        self.env.editorSignals.languageChanged.emit(self, None)

    def insertText(self, text: str):
        self.insert(text)
        line, pos = self.getCursorPosition()
        self.setCursorPosition(line, pos + len(text))

    def modificationStateChange(self, state: bool):
        if self.isPreview:
            return
        tabWidget = self.container.getTabWidget()
        try:
            if state:
                tabWidget.setTabIcon(self.tabid, self.env.documentUnsavedIcon)
            else:
                tabWidget.setTabIcon(self.tabid, self.env.documentSavedIcon)
        except Exception:
            pass

    def textEdited(self):
        if self.isPreview:
            return
        self.isNew = False
        if self._mainWindow is None:
            return
        if self.isUndoAvailable():
            self._mainWindow.undoMenubarItem.setEnabled(True)
        else:
            self._mainWindow.undoMenubarItem.setEnabled(False)
        if self.isRedoAvailable():
            self._mainWindow.redoMenubarItem.setEnabled(True)
        else:
            self._mainWindow.redoMenubarItem.setEnabled(False)

    def editSelectionChanged(self):
        if self.isPreview:
            return
        try:
            if self.hasSelectedText():
                self._mainWindow.cutMenubarItem.setEnabled(True)
                self._mainWindow.copyMenubarItem.setEnabled(True)
                self._mainWindow.deleteMenubarItem.setEnabled(True)
            else:
                self._mainWindow.cutMenubarItem.setEnabled(False)
                self._mainWindow.copyMenubarItem.setEnabled(False)
                self._mainWindow.deleteMenubarItem.setEnabled(False)
        except Exception:
            pass

    def updateCursor(self, line: int, pos: int):
        #self.SendScintilla(QsciScintillaBase.SCI_INDICATORFILLRANGE,0,10)
        self.cursorPosLine = line
        self.cursorPosIndex = pos
        self.updateStatusBar()

    def marginClickCallback(self, margin: int, line: int):
        if margin == 1:
            self.addRemoveBookmark(line)

    def addRemoveBookmark(self, line: int):
        if line in self.bookmarkList:
            self.markerDelete(line, 0)
            self.bookmarkList.remove(line)
        else:
            self.markerAdd(line, 0)
            self.bookmarkList.append(line)

    def updateEolMenu(self) -> None:
        if self.isPreview or self._mainWindow is None:
            return
        self._mainWindow.eolModeWindows.setChecked(False)
        self._mainWindow.eolModeUnix.setChecked(False)
        self._mainWindow.eolModeMac.setChecked(False)
        if self.eolMode() == QsciScintilla.EolMode.EolWindows:
            self._mainWindow.eolModeWindows.setChecked(True)
        elif self.eolMode() == QsciScintilla.EolMode.EolUnix:
            self._mainWindow.eolModeUnix.setChecked(True)
        elif self.eolMode() == QsciScintilla.EolMode.EolMac:
            self._mainWindow.eolModeMac.setChecked(True)

    def changeEolMode(self, mode):
        self.setEolMode(mode)
        self.convertEols(mode)
        self.updateEolMenu()
        self.updateStatusBar()

    def getEolChar(self) -> str:
        if self.eolMode() == QsciScintilla.EolMode.EolWindows:
            return "\r\n"
        elif self.eolMode() == QsciScintilla.EolMode.EolUnix:
            return "\n"
        elif self.eolMode() == QsciScintilla.EolMode.EolMac:
            return "\r"

    def setUsedEncoding(self, encoding: str):
        self.usedEncoding = encoding
        self.updateEncodingMenu()
        self.updateStatusBar()

    def getUsedEncoding(self) -> str:
        return self.usedEncoding

    def getCurrentText(self) -> str:
        if len(self.selectedText()) == 0:
            return self.text()
        else:
            return self.selectedText()

    def setCurrentText(self, text: str) -> None:
        if len(self.selectedText()) == 0:
            self.setText(text)
        else:
            self.replaceSelectedText(text)

    def updateEncodingMenu(self) -> None:
        for i in self.env.encodingActions:
            if i.text() == self.usedEncoding:
                i.setChecked(True)
            else:
                i.setChecked(False)

    def setFilePath(self, path: str) -> None:
        self.filePath = path
        self.updateStatusBar()
        self.pathChanged.emit(path)

    def getFilePath(self) -> str:
        return self.filePath

    def updateMenuActions(self) -> None:
        if self.isPreview or self._mainWindow is None:
            return
        if self.isUndoAvailable():
            self._mainWindow.undoMenubarItem.setEnabled(True)
        else:
            self._mainWindow.undoMenubarItem.setEnabled(False)
        if self.isRedoAvailable():
            self._mainWindow.redoMenubarItem.setEnabled(True)
        else:
            self._mainWindow.redoMenubarItem.setEnabled(False)
        self.editSelectionChanged()
        self.updateEncodingMenu()
        self._mainWindow.updateSelectedLanguage()

    def contextMenuEvent(self, event: QContextMenuEvent):
        if self.isPreview:
            super().contextMenuEvent(event)
            return

        event.setAccepted(False)
        self.env.editorSignals.contextMenu.emit(self, event)
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

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        for i in event.mimeData().urls():
            if i.isLocalFile() and self._mainWindow is not None:
                self._mainWindow.openFile(i.toLocalFile())
        if event.mimeData().text() != "" and len(event.mimeData().urls()) == 0:
            self.insertText(event.mimeData().text())

    def _updateHighlightAllOccurrences(self) -> None:
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, self._highlightOccurrencesIndicator)
        self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, self.length())

        if not self.settings.get("editHighlightOccurrencesSelectedText"):
            return

        highlightedText = self.selectedText().encode("utf-8")

        if len(highlightedText) == 0:
            return

        startLine, startPos, _, _ = self.getSelection()
        currentPos = self.positionFromLineIndex(startLine, startPos)

        for pos in findAllText(self.text().encode("utf-8"), highlightedText):
            if pos != currentPos:
                self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, pos, len(highlightedText))

    def getSaveMetaData(self) -> dict[str, Any]:
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
            except Exception:
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
            "customTabName": self.customTabName,
            "fileChangedBannerVisible": fileChangedBannerVisible,
            "modificationTime": modificationTime,
        }
        self.env.editorSignals.saveSession.emit(self, data)
        return data

    def restoreSaveMetaData(self, data: dict[str, Any]) -> None:
        path = data.get("path", "")
        self.setFilePath(path)
        self.setModified(data["modified"])
        self.setUsedEncoding(data.get("encoding", self.settings.defaultEncoding))
        syntax = data.get("language", "")
        if syntax != "":
            for l in self.env.languageList:
                if l.getID() == syntax:
                    self.setLanguage(l)
        self.bookmarkList = data.get("bookmarks", [])
        for line in self.bookmarkList:
            self.markerAdd(line, 0)
        self.setCursorPosition(data["cursorPosLine"], data["cursorPosIndex"])
        self.zoomTo(data.get("zoom", self.settings.defaultZoom))
        self.custom_settings = data.get("customSettings", {})
        self.settings.loadDict(self.custom_settings)
        if len(self.custom_settings) != 0:
            self.updateSettings(self.settings)
        self.setOverwriteMode(data.get("overwriteMode", False))
        modificationTime = data.get("modificationTime", 0)
        if self.container:
            if not os.path.exists(path) and path != "":
                self.container.showFileDeletedBanner()
            elif data.get("fileChangedBannerVisible", False):
                self.container.showFileChangedBanner()
            elif modificationTime != 0:
                if modificationTime != os.path.getmtime(path):
                    self.container.showFileChangedBanner()
        self.customTabName = data.get("customTabName", "")
        self.env.editorSignals.restoreSession.emit(self, data)

    def loadEditorConfig(self):
        """
        Loads a .editorconfig file
        """
        try:
            config = editorconfig.get_properties(self.getFilePath())
        except NameError:
            self.env.logger.critical("Trying to load a file with editorconfig enabled while the editorconfig module is not installed")
            return
        except Exception:
            self.env.logger.error("Error occurred while getting .editorconfig properties")
            return
        if "indent_style" in config and self.settings.editorConfigUseIndentStyle:
            if config["indent_style"] == "space":
                self.custom_settings["editTabSpaces"] = True
            elif config["indent_style"] == "tab":
                self.custom_settings["editTabSpaces"] = False
        if self.settings.editorConfigTabWidth:
            try:
                self.custom_settings["editTabWidth"] = int(config["indent_size"])
            except Exception:
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
            self.container.showBanner(EditorconfigBanner(self.container))

    def setCustomTheme(self, theme: Optional["ThemeBase"]) -> None:
        self._customTheme = theme
        self.updateSettings(self.settings)

    def changeFont(self, font: QFont, settings: "Settings"):
        self.setFont(font)
        self.setMarginsFont(font)
        fontmetrics = QFontMetrics(font)
        if settings.editShowLineNumbers:
            self.setMarginWidth(0, fontmetrics.averageCharWidth() * 6)
        else:
            self.setMarginWidth(0, 0)
        if self.currentLexer:
            self.currentLexer.setFont(font)
            self.currentLexer.setDefaultFont(font)

    def setSettings(self, settings: "Settings"):
        settings = copy.copy(settings)
        settings.loadDict(self.custom_settings)
        self.updateSettings(settings)
        self.env.editorSignals.settingsChanged.emit(self, settings)

    def updateSettings(self, settings: "Settings"):
        if self._customTheme is not None:
            try:
                self._customTheme.applyTheme(self, self.currentLexer)
            except Exception as ex:
                self.env.logger.exception(ex)
                self.env.themes["builtin.default"].applyTheme(self, self.currentLexer)
        else:
            if settings.get("editTheme") in self.env.themes:
                try:
                    self.env.themes[settings.get("editTheme")].applyTheme(self, self.currentLexer)
                except Exception as ex:
                    self.env.logger.exception(ex)
                    self.env.themes["builtin.default"].applyTheme(self, self.currentLexer)
            else:
                self.env.logger.warning("The selected Theme could not be found. Falling back to the default Theme.")
                self.env.themes["builtin.default"].applyTheme(self, self.currentLexer)

        if settings.useCustomFont:
            self.changeFont(settings.get("editFont"), settings)
        else:
            self.changeFont(QFont(), settings)
        self.setFolding(self.foldStyles[settings.get("editFoldStyle")])
        self.setCaretLineVisible(settings.get("highlightCurrentLine"))
        self.setTabWidth(settings.get("editTabWidth"))
        self.setIndentationsUseTabs(not settings.get("editTabSpaces"))
        if settings.get("editTextWrap"):
            self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        else:
            self.setWrapMode(QsciScintilla.WrapMode.WrapNone)
        if settings.get("editShowWhitespaces"):
            self.setWhitespaceVisibility(QsciScintilla.WhitespaceVisibility.WsVisible)
        else:
            self.setWhitespaceVisibility(QsciScintilla.WhitespaceVisibility.WsInvisible)
        self.setAutoIndent(settings.get("editAutoIndent"))
        self.setEolVisibility(settings.get("editShowEol"))
        self.setIndentationGuides(settings.get("showIndentationGuides"))
        if settings.enableAutocompletion:
            if settings.autocompletionUseDocument and settings.get("autocompletionUseAPI"):
                self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
            elif settings.get("autocompletionUseDocument"):
                self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsDocument)
            elif settings.get("autocompletionUseAPI"):
                self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAPIs)
            else:
                self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsNone)
            self.setAutoCompletionCaseSensitivity(settings.get("autocompletionCaseSensitive"))
            self.setAutoCompletionThreshold(settings.get("autocompleteThreshold"))
            self.setAutoCompletionReplaceWord(settings.get("autocompletionReplaceWord"))
            if self.currentLexer and settings.get("autocompletionUseAPI") and self.language:
                self.language.getAPI(self.currentLexer)
        else:
            self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsNone)
        self.settings = settings
        self._updateHighlightAllOccurrences()

    def positionFromPoint(self, point: QPoint) -> int:
        return self.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINTCLOSE, point.x(), point.y())

    def isBigFile(self) -> bool:
        return self.bigFile

    def getIndicatorNumber(self) -> int:
        self.currentIndicatorNumber += 1
        return self.currentIndicatorNumber - 1

    def getLanguage(self) -> Optional[LanguageBase]:
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
        if self._mainWindow is None:
            return
        self.updateEolMenu()
        self.updateStatusBar()
        self.updateMenuActions()
        self._mainWindow.updateWindowTitle()
        if self._mainWindow.currentMacro:
            self._mainWindow.stopMacroRecording()
            macro = self._mainWindow.currentMacro.save()
            self._mainWindow.currentMacro = QsciMacro(self)
            self._mainWindow.currentMacro.load(macro)

    def focusInEvent(self, event: QFocusEvent):
        if self.container is not None:
            self.container.getTabWidget().markWidgetAsActive()
            self.updateOtherWidgets()
        super().focusInEvent(event)
