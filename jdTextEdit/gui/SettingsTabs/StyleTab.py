from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton, QFontDialog, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QSlider
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from jdTextEdit.gui.CodeEdit import CodeEdit
from jdTextEdit.Settings import Settings
from PyQt5.Qsci import QsciLexerLua

class StyleTab(QWidget,SettingsTabBase):
    def __init__(self,env):
        super().__init__()
        self.font = QFont()
        self.env = env

        self.themeSelect = QComboBox()
        self.foldSelect = QComboBox()
        self.fontCheckBox = QCheckBox(env.translate("settingsWindow.style.checkBox.font"))
        self.fontButton = QPushButton()
        self.lineNumberCheckBox = QCheckBox(env.translate("settingsWindow.style.checkBox.showLineNumbers"))
        self.highlightLineCheckBox = QCheckBox(env.translate("settingsWindow.style.checkBox.highlightCurrentLine"))
        self.zoomSlider = QSlider(Qt.Horizontal)
        self.editorPreview = CodeEdit(env,preview=True)

        for key, value in env.themes.items():
            self.themeSelect.addItem(value.getName(),key)

        self.foldSelect.addItem(env.translate("settingsWindow.style.foldStyle.none"))
        self.foldSelect.addItem(env.translate("settingsWindow.style.foldStyle.plain"))
        self.foldSelect.addItem(env.translate("settingsWindow.style.foldStyle.circled"))
        self.foldSelect.addItem(env.translate("settingsWindow.style.foldStyle.boxed"))
        self.foldSelect.addItem(env.translate("settingsWindow.style.foldStyle.circledTree"))
        self.foldSelect.addItem(env.translate("settingsWindow.style.foldStyle.boxedTree"))

        self.zoomSlider.setMaximum(20)
        self.zoomSlider.setMinimum(-10)
        self.zoomSlider.setTickInterval(5)
        self.zoomSlider.setTickPosition(QSlider.TicksBelow)
        self.zoomSlider.valueChanged.connect(lambda: self.editorPreview.zoomTo(self.zoomSlider.value()))

        previewText = ("local var = true\n\n"
                       "function example(a,b)\n"
                       "    if a == b then\n"
                       '        return "success"\n'
                       "    else\n"
                       "        return 0\nend")

        self.themeSelect.currentIndexChanged.connect(lambda: self.updatePreviewEdit())
        self.foldSelect.currentIndexChanged.connect(self.updatePreviewEdit)
        self.fontCheckBox.stateChanged.connect(self.fontCheckBoxChanged)
        self.fontButton.clicked.connect(self.fontButtonClicked)
        self.lineNumberCheckBox.stateChanged.connect(self.updatePreviewEdit)
        self.highlightLineCheckBox.stateChanged.connect(self.updatePreviewEdit)
        self.editorPreview.setText(previewText)
        self.editorPreview.setLexer(QsciLexerLua())

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(env.translate("settingsWindow.style.label.theme")),0,0)
        gridLayout.addWidget(self.themeSelect,0,1)
        gridLayout.addWidget(QLabel(env.translate("settingsWindow.style.label.foldStyle")),1,0)
        gridLayout.addWidget(self.foldSelect,1,1)
        gridLayout.addWidget(self.fontCheckBox,2,0)
        gridLayout.addWidget(self.fontButton,2,1)

        zoomLayout = QHBoxLayout()
        zoomLayout.addWidget(QLabel(env.translate("settingsWindow.style.label.defaultZoom")))
        zoomLayout.addStretch()
        zoomLayout.addWidget(self.zoomSlider)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addWidget(self.lineNumberCheckBox)
        mainLayout.addWidget(self.highlightLineCheckBox)
        mainLayout.addLayout(zoomLayout)
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

    def updatePreviewEdit(self):
        self.editorPreview.setSettings(self.getSettings(Settings(defaultSettings=self.env.defaultSettings)))

    def updateTab(self, settings):
        for i in range(self.themeSelect.count()):
            if self.themeSelect.itemData(i) == settings.editTheme:
                self.themeSelect.setCurrentIndex(i)
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
        self.zoomSlider.setValue(settings.defaultZoom)
        self.editorPreview.zoomTo(settings.defaultZoom)
        self.updatePreviewEdit()

    def getSettings(self, settings):
        settings.editTheme = self.themeSelect.itemData(self.themeSelect.currentIndex())
        settings.editFoldStyle = self.foldSelect.currentIndex()
        settings.useCustomFont = bool(self.fontCheckBox.checkState())
        settings.editFont = self.font
        settings.editShowLineNumbers = bool(self.lineNumberCheckBox.checkState())
        settings.highlightCurrentLine = bool(self.highlightLineCheckBox.checkState())
        settings.defaultZoom = self.zoomSlider.value()
        return settings

    def title(self):
        return self.env.translate("settingsWindow.style")
