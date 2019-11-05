from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton, QFontDialog, QGridLayout, QVBoxLayout, QComboBox, QLabel
from PyQt5.QtGui import QFont
from jdTextEdit.gui.CodeEdit import CodeEdit
from jdTextEdit.Settings import Settings
from PyQt5.Qsci import QsciLexerLua

class StyleTab(QWidget):
    def __init__(self,env):
        super().__init__()
        self.font = QFont()

        #self.styleSelect = QComboBox()
        self.foldSelect = QComboBox()
        self.fontCheckBox = QCheckBox(env.translate("settingsWindow.style.checkBox.font"))
        self.fontButton = QPushButton()
        self.lineNumberCheckBox = QCheckBox(env.translate("settingsWindow.style.checkBox.showLineNumbers"))
        self.highlightLineCheckBox = QCheckBox(env.translate("settingsWindow.style.checkBox.highlightCurrentLine"))
        self.editorPreview = CodeEdit(env,preview=True)

        #self.styleSelect.addItem("Default")
        #for key, value in env.styles.items():
        #    self.styleSelect.addItem(key)

        self.foldSelect.addItem(env.translate("settingsWindow.style.foldStyle.none"))
        self.foldSelect.addItem(env.translate("settingsWindow.style.foldStyle.plain"))
        self.foldSelect.addItem(env.translate("settingsWindow.style.foldStyle.circled"))
        self.foldSelect.addItem(env.translate("settingsWindow.style.foldStyle.boxed"))
        self.foldSelect.addItem(env.translate("settingsWindow.style.foldStyle.circledTree"))
        self.foldSelect.addItem(env.translate("settingsWindow.style.foldStyle.boxedTree"))

        previewText = ("local var = true\n\n"
                       "function example(a,b)\n"
                       "    if a == b then\n"
                       '        return "success"\n'
                       "    else\n"
                       "        return 0\nend")

        #self.styleSelect.currentIndexChanged.connect(lambda: self.updatePreviewEdit())
        self.foldSelect.currentIndexChanged.connect(self.updatePreviewEdit)
        self.fontCheckBox.stateChanged.connect(self.fontCheckBoxChanged)
        self.fontButton.clicked.connect(self.fontButtonClicked)
        self.lineNumberCheckBox.stateChanged.connect(self.updatePreviewEdit)
        self.highlightLineCheckBox.stateChanged.connect(self.updatePreviewEdit)
        self.editorPreview.setText(previewText)
        self.editorPreview.setSyntaxHighlighter(QsciLexerLua())

        gridLayout = QGridLayout()
        #gridLayout.addWidget(QLabel(env.translate("settingsWindow.style.label.style")),0,0)
        #gridLayout.addWidget(self.styleSelect,0,1)
        gridLayout.addWidget(QLabel(env.translate("settingsWindow.style.label.foldStyle")),1,0)
        gridLayout.addWidget(self.foldSelect,1,1)
        gridLayout.addWidget(self.fontCheckBox,2,0)
        gridLayout.addWidget(self.fontButton,2,1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addWidget(self.lineNumberCheckBox)
        mainLayout.addWidget(self.highlightLineCheckBox)
        mainLayout.addWidget(self.editorPreview)

        self.setLayout(mainLayout)

    def fontCheckBoxChanged(self):
        if self.fontCheckBox.checkState():
            self.fontButton.setEnabled(True)
        else:
            self.fontButton.setEnabled(False)
        self.updatePreviewEdit()

    def fontButtonClicked(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.fontButton.setText(font.family())
            self.font = font
            self.updatePreviewEdit()

    def updateTab(self, settings):
        #for i in range(self.styleSelect.count()):
        #    if self.styleSelect.itemText(i) == settings.editStyle:
        #        self.styleSelect.setCurrentIndex(i)
        self.foldSelect.setCurrentIndex(settings.editFoldStyle)
        self.font = settings.editFont
        self.fontCheckBox.setChecked(settings.useCustomFont)
        if settings.useCustomFont:
            self.fontButton.setEnabled(True)
        else:
            self.fontButton.setEnabled(False)
        self.fontButton.setText(self.font.family())
        self.lineNumberCheckBox.setChecked(settings.editShowLineNumbers)     
        self.highlightLineCheckBox.setChecked(settings.highlightCurrentLine)
        self.updatePreviewEdit()

    def getSettings(self, settings):
        #settings.editStyle = self.styleSelect.currentText()
        settings.editFoldStyle = self.foldSelect.currentIndex()
        settings.useCustomFont = bool(self.fontCheckBox.checkState())
        settings.editFont = self.font
        settings.editShowLineNumbers = bool(self.lineNumberCheckBox.checkState())
        settings.highlightCurrentLine = bool(self.highlightLineCheckBox.checkState())
        return settings

    def updatePreviewEdit(self):
        self.editorPreview.updateSettings(self.getSettings(Settings()))
        
