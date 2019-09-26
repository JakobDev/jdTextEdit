from PyQt5.QtWidgets import QMenu
from PyQt5.Qsci import QsciScintilla, QsciLexer, QsciAPIs, QsciScintillaBase
from PyQt5.QtGui import QColor, QFontMetrics, QFont, QCursor
from AutocompleteXML import AutocompleteXML
import os

class CodeEdit(QsciScintilla):
    ARROW_MARKER_NUM = 8
    def __init__(self,env,preview=False,isNew=False):
        super().__init__()
        self.env = env
        self.isPreview = preview
        self.isNew = isNew
        self.currentLexer = None
        self.apiCompletion = None
        self.searchText = ""
        self.tabid = None
        self.foldStyles = [QsciScintilla.NoFoldStyle,QsciScintilla.PlainFoldStyle,QsciScintilla.CircledFoldStyle,QsciScintilla.BoxedFoldStyle,QsciScintilla.CircledTreeFoldStyle,QsciScintilla.BoxedTreeFoldStyle]
        self.updateSettings(env.settings)
        self.setMarginLineNumbers(0, True)
        self.setUtf8(True)
        self.modificationChanged.connect(self.modificationStateChange)
        #self.modificationStateChange(False)
        #self.setMarginsBackgroundColor(QColor("#cccccc"))

        self.textChanged.connect(self.textEdited)
        self.selectionChanged.connect(self.editSelectionChanged)
        self.cursorPositionChanged.connect(self.updateCursor)

    def setSyntaxHighlighter(self, lexer, lexerList=None):
        #self.lexer() is a little bit buggy
        self.currentLexer = lexer
        self.setLexer(lexer)
        if lexerList:
            if isinstance(lexerList[3], str):
                if os.path.isfile(os.path.join(self.env.programDir,"autocompletion",lexerList[3] + ".xml")):
                    self.apiCompletion = os.path.join(self.env.programDir,"autocompletion",lexerList[3] + ".xml")               
                else:
                    self.apiCompletion = None
            else:
                self.apiCompletion = lexerList[3]
        else:
            self.apiCompletion = None
        self.updateSettings(self.env.settings)
        
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
        if not self.isPreview:
            self.env.mainWindow.cursorPosLabel.setText(self.env.translate("mainWindow.statusBar.cursorPosLabel") % (line + 1, pos + 1))

    def updateEolMenu(self):
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

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        for i in self.env.settings.editContextMenu:
            if i == "separator":
                menu.addSeparator()
            else:
                menu.addAction(self.env.menuActions[i])
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
