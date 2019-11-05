from PyQt5.QtWidgets import QMenu
from PyQt5.Qsci import QsciScintilla, QsciLexer, QsciAPIs, QsciScintillaBase
from PyQt5.QtGui import QColor, QFontMetrics, QFont, QCursor
from jdTextEdit.AutocompleteXML import AutocompleteXML
from jdTextEdit.LexerList import getLexerList
import os

class CodeEdit(QsciScintilla):
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
        self.cursorPosString = env.translate("mainWindow.statusBar.cursorPosLabel") % (1,1)
        self.lexerName = env.translate("mainWindow.menu.language.plainText")
        self.foldStyles = [QsciScintilla.NoFoldStyle,QsciScintilla.PlainFoldStyle,QsciScintilla.CircledFoldStyle,QsciScintilla.BoxedFoldStyle,QsciScintilla.CircledTreeFoldStyle,QsciScintilla.BoxedTreeFoldStyle]
        eolModeList = [QsciScintilla.EolWindows,QsciScintilla.EolUnix,QsciScintilla.EolMac]
        self.changeEolMode(eolModeList[self.env.settings.defaultEolMode])
        self.updateSettings(env.settings)
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

        if self.env.settings.defaultLanguage != -1:
            lexerList = getLexerList()
            self.setSyntaxHighlighter(lexerList[self.env.settings.defaultLanguage]["lexer"](),lexerList[self.env.settings.defaultLanguage])

        self.setMarginType(1, QsciScintilla.SymbolMargin)
        sym_4 = QsciScintilla.Circle
        self.markerDefine(sym_4, 0)
        #self.setMarginWidth(1, 10)

    def updateStatusBar(self):
        if self.isPreview or not hasattr(self.env,"mainWindow"):
            return
        self.env.mainWindow.pathLabel.setText(self.filePath)
        self.env.mainWindow.encodingLabel.setText(self.usedEncoding)
        self.env.mainWindow.lexerLabel.setText(self.lexerName)
        self.env.mainWindow.cursorPosLabel.setText(self.cursorPosString)

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
        self.updateSettings(self.env.settings)
        if not self.isPreview:
            self.lexerName = str(lexer.language())
            self.updateStatusBar()
 
    def removeSyntaxHighlighter(self):
        self.setLexer(None)
        self.currentLexer = None
        self.updateSettings(self.env.settings)
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

    def contextMenuEvent(self, event):
        menu = QMenu("jdTextEdit",self)
        for i in self.env.settings.editContextMenu:
            if i == "separator":
                menu.addSeparator()
            else:
                if i in self.env.menuActions:
                    menu.addAction(self.env.menuActions[i])
        menu.setTearOffEnabled(True)
        menu.popup(QCursor.pos())

    def setDefaultStyle(self):
        #self.resetSelectionBackgroundColor()
        #self.resetSelectionForegroundColor()
        self.setColor(QColor("#000000"))
        self.setPaper(QColor("#FFFFFF"))
        self.setSelectionForegroundColor(QColor("#FFFFFF"))
        self.setSelectionBackgroundColor(QColor("#308CC6"))
        self.setMarginsBackgroundColor(QColor("#cccccc"))
        self.setCaretLineBackgroundColor(QColor("#FFFF00"))
        #self.resetMarginsBackgroundColor()
        #self.resetCaretLineBackgroundColor()

    def setSingleColor(self,func,style,name,styleNum=None):
        if name in style:
            try:
                c = QColor(style[name])
                c.setAlpha(255)
                if styleNum:
                    func(c,styleNum)
                else:
                    func(c)
            except Exception as e:
                print(e)

    def setCustomStyle(self,style):
        self.setSingleColor(self.setColor,style,"textColor")
        self.setSingleColor(self.setPaper,style,"paperColor")
        self.setSingleColor(self.setSelectionForegroundColor,style,"selectionForegroundColor")
        self.setSingleColor(self.setSelectionBackgroundColor,style,"selectionBackgroundColor")
        #self.setSelectionBackgroundColor(QColor(100,100,100,100))
        self.setSingleColor(self.setMarginsBackgroundColor,style,"marginsBackgroundColor")
        self.setSingleColor(self.setCaretLineBackgroundColor,style,"caretLineBackgroundColor")
        #self.setMarginsBackgroundColor(QColor(style["marginsBackgroundColor"]))
        #self.setCaretLineBackgroundColor(QColor(style["caretLineBackgroundColor"]))
        if self.currentLexer:
            self.setSingleColor(self.currentLexer.setDefaultColor,style,"textColor")
            self.setSingleColor(self.currentLexer.setDefaultPaper,style,"paperColor")
            self.setSingleColor(self.currentLexer.setColor,style,"textColor",styleNum=0)
            self.setSingleColor(self.currentLexer.setColor,style,"selectionBackgroundColor",styleNum=1)
            self.setSingleColor(self.currentLexer.setPaper,style,"paperColor",styleNum=0)
            #self.currentLexer.setDefaultColor()

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

    def updateSettings(self, settings):
        #if settings.editStyle == "Default":
        #    self.setDefaultStyle()
        #else:
        #    self.setCustomStyle(self.env.styles[settings.editStyle])
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
