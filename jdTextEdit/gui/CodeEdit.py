from PyQt5.QtWidgets import QMenu
from PyQt5.Qsci import QsciScintilla, QsciLexer, QsciAPIs, QsciScintillaBase
from PyQt5.QtGui import QColor, QFontMetrics, QFont, QCursor
from PyQt5.QtCore import pyqtSignal
from jdTextEdit.AutocompleteXML import AutocompleteXML
from jdTextEdit.LexerList import getLexerList
import editorconfig
import copy
import os

class CodeEdit(QsciScintilla):
    pathChanged = pyqtSignal("QString")
    def __init__(self,env,preview=None,isNew=False):
        super().__init__()
        self.env = env
        self.isPreview = preview
        self.isNew = isNew
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
        self.cursorPosString = env.translate("mainWindow.statusBar.cursorPosLabel") % (1,1)
        self.lexerName = env.translate("mainWindow.menu.language.plainText")
        self.foldStyles = [QsciScintilla.NoFoldStyle,QsciScintilla.PlainFoldStyle,QsciScintilla.CircledFoldStyle,QsciScintilla.BoxedFoldStyle,QsciScintilla.CircledTreeFoldStyle,QsciScintilla.BoxedTreeFoldStyle]
        eolModeList = [QsciScintilla.EolWindows,QsciScintilla.EolUnix,QsciScintilla.EolMac]
        self.changeEolMode(eolModeList[self.settings.defaultEolMode])
        self.updateSettings(self.settings)
        self.setMarginLineNumbers(0, True)
        self.setUtf8(True)
        self.modificationChanged.connect(self.modificationStateChange)
        self.marginClicked.connect(self.marginClickCallback)
        self.setMarginSensitivity(1,True)
        #self.modificationStateChange(False)
        #self.setMarginsBackgroundColor(QColor("#cccccc"))
        #self.setWrapVisualFlags(QsciScintilla.WrapFlagByText)

        self.textChanged.connect(self.textEdited)
        self.selectionChanged.connect(self.editSelectionChanged)
        self.cursorPositionChanged.connect(self.updateCursor)

        if self.settings.defaultLanguage != -1:
            lexerList = getLexerList()
            self.setSyntaxHighlighter(lexerList[self.settings.defaultLanguage]["lexer"](),lexerList[self.settings.defaultLanguage])

        self.setMarginType(1, QsciScintilla.SymbolMargin)
        sym_4 = QsciScintilla.Circle
        self.markerDefine(sym_4, 0)
        #self.setMarginWidth(1, 10)

        self.zoomTo(self.settings.defaultZoom)

    def updateStatusBar(self):
        if self.isPreview or not hasattr(self.env,"mainWindow"):
            return
        self.env.mainWindow.pathLabel.setText(self.filePath)
        self.env.mainWindow.encodingLabel.setText(self.usedEncoding)
        self.env.mainWindow.lexerLabel.setText(self.lexerName)
        self.env.mainWindow.cursorPosLabel.setText(self.cursorPosString)
        if self.eolMode() == QsciScintilla.EolWindows:
            self.env.mainWindow.eolLabel.setText("CRLF")
        elif self.eolMode() == QsciScintilla.EolUnix:
            self.env.mainWindow.eolLabel.setText("LF")
        elif self.eolMode() == QsciScintilla.EolMac:
            self.env.mainWindow.eolLabel.setText("CR")

    def setSyntaxHighlighter(self, lexer, lexerList=None):
        #self.lexer() is a little bit buggy
        self.currentLexer = lexer
        self.setLexer(lexer)
        if lexerList:
            if isinstance(lexerList["xmlapi"], str):
                if os.path.isfile(os.path.join(self.env.programDir,"autocompletion",lexerList["xmlapi"] + ".xml")):
                    self.apiCompletion = os.path.join(self.env.programDir,"autocompletion",lexerList["xmlapi"] + ".xml")               
                else:
                    self.apiCompletion = None
            else:
                self.apiCompletion = lexerList["xmlapi"]
        else:
            self.apiCompletion = None
        self.updateSettings(self.settings)
        #self.setLexerColor(lexer,self.env.themes[self.settings.editTheme]["colors"])
        if not self.isPreview:
            self.lexerName = str(lexer.language())
            self.updateStatusBar()
            if not hasattr(self.env,"mainWindow"):
                return
            self.env.mainWindow.updateSelectedLanguage()
 
    def removeSyntaxHighlighter(self):
        self.setLexer(None)
        self.currentLexer = None
        self.updateSettings(self.settings)
        self.lexerName = self.env.translate("mainWindow.menu.language.plainText")
        self.updateStatusBar()

    def insertText(self, text):
        self.insert(text)
        line, pos = self.getCursorPosition()
        self.setCursorPosition(line,pos + len(text))

    def modificationStateChange(self, state):
        if self.isPreview:
            return
        #self.isNew = False
        try:
            if state:
                self.env.mainWindow.tabWidget.setTabIcon(self.tabid,self.env.documentUnsavedIcon)
            else:
                self.env.mainWindow.tabWidget.setTabIcon(self.tabid,self.env.documentSavedIcon)
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
        if self.eolMode() == QsciScintilla.EolWindows:
            self.env.mainWindow.eolModeWindows.setChecked(True)
        elif self.eolMode() == QsciScintilla.EolUnix:
            self.env.mainWindow.eolModeUnix.setChecked(True)
        elif self.eolMode() == QsciScintilla.EolMac:
            self.env.mainWindow.eolModeMac.setChecked(True)

    def changeEolMode(self, mode):
        self.setEolMode(mode)
        self.convertEols(mode)
        self.updateEolMenu()
        self.updateStatusBar()

    def getEolChar(self):
        if self.eolMode() == QsciScintilla.EolWindows:
            return "\r\n"
        elif self.eolMode() == QsciScintilla.EolUnix:
            return "\n"
        elif self.eolMode() == QsciScintilla.EolMac:
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

    def setSingleLexerColor(self,lexer,color,name):
        if isinstance(name,list):
            for i in name:
                try:
                    lexer.setColor(QColor(color), getattr(lexer,i))
                except:
                    pass
        else:
            try:
                lexer.setColor(QColor(color), getattr(lexer,name))
            except:
                print(lexer,name)
                pass

    def getSaveMetaData(self):
        if self.currentLexer:
            syntax = self.currentLexer.language()
        else:
            syntax = ""
        return {
            "path": self.getFilePath(),
            "modified": self.isModified(),
            "language": syntax,
            "encoding": self.getUsedEncoding(),
            "bookmarks": self.bookmarkList,
            "cursorPosLine": self.cursorPosLine,
            "cursorPosIndex": self.cursorPosIndex,
            "zoom": self.SendScintilla(QsciScintillaBase.SCI_GETZOOM),
            "customSettings": self.custom_settings
        }

    def restoreSaveMetaData(self,data):
        self.setFilePath(data.get("path",""))
        self.setModified(data["modified"])
        self.setUsedEncoding(data.get("encoding",self.settings.defaultEncoding))
        for l in self.env.lexerList:
            s = l["lexer"]()
            if s.language() == data["language"]:
                self.setSyntaxHighlighter(s,lexerList=l)
        self.bookmarkList = data.get("bookmarks",[])
        for line in self.bookmarkList:
            self.markerAdd(line,0)
        self.setCursorPosition(data["cursorPosLine"],data["cursorPosIndex"])
        self.zoomTo(data.get("zoom",self.settings.defaultZoom))
        self.custom_settings = data.get("customSettings",{})
        self.settings.loadDict(self.custom_settings)
        if len(self.custom_settings) != 0:
            self.updateSettings(self.settings)

    def loadEditorConfig(self):
        try:
            config = editorconfig.get_properties(self.getFilePath())
        except:
            print("Error occurred while getting .editorconfig properties")
            return
        if "indent_style" in config:
            if config["indent_style"] == "space":
                self.custom_settings["editTabSpaces"] = True
            elif config["indent_style"] == "tab":
                self.custom_settings["editTabSpaces"] = False
        try:
            self.custom_settings["editTabWidth"] = int(config["indent_size"])
        except:
            pass
        if "tab_width" in config:
            self.custom_settings["editTabWidth"] = int(config["tab_width"])
        if "end_of_line" in config:
            if config["end_of_line"] == "crlf":
                self.custom_settings["defaultEolMode"] = 0
            elif config["end_of_line"] == "lf":
                self.custom_settings["defaultEolMode"] = 1
            elif config["end_of_line"] == "cr":
                self.custom_settings["defaultEolMode"] = 2
        if "trim_trailing_whitespace" in config:
            if config["trim_trailing_whitespace"] == "true":
                self.custom_settings["stripSpacesSave"] = True
            elif config["trim_trailing_whitespace"] == "false":
                self.custom_settings["stripSpacesSave"] = False
        if "insert_final_newline" in config:
            if config["insert_final_newline"] == "true":
                self.custom_settings["eolFileEnd"] = True
            elif config["insert_final_newline"] == "false":
                self.custom_settings["eolFileEnd"] = False
        self.settings.loadDict(self.custom_settings)
        self.updateSettings(self.settings)

    def setLexerColor_Old(self,lexer,style):
        #return
        lexer.setPaper(QColor(style.get("paperColor","#FFFFFF")))
        lexer.setDefaultPaper(QColor(style.get("paperColor","#FFFFFF")))
        lexer.setDefaultColor(QColor(style.get("textColor","#000000")))
        #vars(lexer) just returns a empty dict
        self.setSingleLexerColor(lexer,style.get("textColor","#000000"),[
        "Default",
        "JavaScriptDefault",
        "JavaScriptWord"
        ])
        self.setSingleLexerColor(lexer,style.get("classNameColor","#0000ff"),"ClassName")
        self.setSingleLexerColor(lexer,style.get("keywordColor","#00007f"),[
        "Keyword",
        "JavaScriptKeyword"
        ])
        self.setSingleLexerColor(lexer,style.get("commentColor","#007f00"),[
            "Comment",
            "LineComment",
            "JavaScriptComment",
            "JavaScriptCommentDoc",
            "JavaScriptCommentLine",
            "HTMLComment"
        ])
        self.setSingleLexerColor(lexer,style.get("numberColor","#007f7f"),[
        "Number",
        "JavaScriptNumber"
        ])
        self.setSingleLexerColor(lexer,style.get("stringColor","#7f007f"),[
            "String",
            "UnclosedString",
            "DoubleQuotedString",
            "TripleSingleQuotedString",
            "TripleDoubleQuotedString",
            "PHPSingleQuotedString",
            "PHPDoubleQuotedString",
            "HTMLSingleQuotedString",
            "HTMLDoubleQuotedString",
            "JavaScriptSingleQuotedString",
            "JavaScriptDoubleQuotedString",
            "JavaScriptUnclosedString"
        ])
        self.setSingleLexerColor(lexer,style.get("functionNameColor","#007f7f"),[
            "BasicFunctions",
            "FunctionMethodName"
        ])
        self.setSingleLexerColor(lexer,style.get("operatorColor","#000000"),"Operator")
        self.setSingleLexerColor(lexer,style.get("identifierColor","#000000"),"Identifier")
        self.setSingleLexerColor(lexer,style.get("tagColor","#cc0000"),"Tag")
        '''
        try:
            lexer.setColor(QColor("#F1E607"), lexer.CommentBlock)
        except:
            pass
        try:
            lexer.setColor(QColor("#F1E607"), lexer.HighlightedIdentifier)
        except:
            pass
        try:
            lexer.setColor(QColor("#F1E607"), lexer.Decorator)
        except:
            pass
        '''

    def setCustomStyle(self,style):
        #return
        self.setColor(QColor(style.get("textColor","#000000")))
        self.setPaper(QColor(style.get("paperColor","#FFFFFF")))
        self.setSelectionForegroundColor(QColor(style.get("selectionForegroundColor","#FFFFFF")))
        self.setSelectionBackgroundColor(QColor(style.get("selectionBackgroundColor","#308CC6")))
        self.setMarginsBackgroundColor(QColor(style.get("marginsBackgroundColor","#cccccc")))
        self.setMarginsForegroundColor(QColor(style.get("marginsForegroundColor","#000000")))
        self.setCaretLineBackgroundColor(QColor(style.get("caretLineBackgroundColor","#ffff00")))
        if self.currentLexer:
           self.setLexerColor(self.currentLexer,style)

    def changeFont(self,font,settings):
        self.setFont(font)
        self.setMarginsFont(font)
        fontmetrics = QFontMetrics(font)
        if settings.editShowLineNumbers:
            self.setMarginWidth(0, fontmetrics.width("00000") + 6)
        else:
            pass
            self.setMarginWidth(0,0)
        if self.currentLexer:
            self.currentLexer.setFont(font)
            self.currentLexer.setDefaultFont(font)

    def setSettings(self, settings):
        settings = copy.copy(settings)
        settings.loadDict(self.custom_settings)
        self.updateSettings(settings)

    def updateSettings(self, settings):
        #self.setCustomStyle(self.env.themes[settings.editTheme]["colors"])
        if settings.useCustomFont:
            self.changeFont(settings.editFont,settings)
        else:
            self.changeFont(QFont(),settings)
        self.setFolding(self.foldStyles[settings.editFoldStyle])
        self.setCaretLineVisible(settings.highlightCurrentLine)
        self.setTabWidth(settings.editTabWidth)
        self.setIndentationsUseTabs(not settings.editTabSpaces)
        self.setWrapMode(settings.editTextWrap)
        self.setWhitespaceVisibility(settings.editShowWhitespaces)
        self.setAutoIndent(settings.editAutoIndent)
        self.setEolVisibility(settings.editShowEol)
        self.setIndentationGuides(settings.showIndentationGuides)
        if settings.enableAutocompletion:
            if settings.autocompletionUseDocument and settings.autocompletionUseAPI:
                self.setAutoCompletionSource(QsciScintilla.AcsAll)
            elif settings.autocompletionUseDocument:
                self.setAutoCompletionSource(QsciScintilla.AcsDocument)
            elif settings.autocompletionUseAPI:
                self.setAutoCompletionSource(QsciScintilla.AcsAPIs)
            else:
                self.setAutoCompletionSource(QsciScintilla.AcsNone)
            self.setAutoCompletionCaseSensitivity(settings.autocompletionCaseSensitive)
            self.setAutoCompletionThreshold(settings.autocompleteThreshold)
            self.setAutoCompletionReplaceWord(settings.autocompletionReplaceWord)
            if self.currentLexer and settings.autocompletionUseAPI and self.apiCompletion:
                if isinstance(self.apiCompletion, str):
                    api = AutocompleteXML(self.currentLexer,self.apiCompletion)
                else:
                    api = self.apiCompletion(self.currentLexer)
        else:
            self.setAutoCompletionSource(QsciScintilla.AcsNone)
        self.settings = settings
