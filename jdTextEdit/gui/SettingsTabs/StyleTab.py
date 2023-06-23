from PyQt6.QtWidgets import QWidget, QCheckBox, QPushButton, QFontDialog, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QSlider
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt6.QtCore import Qt, QCoreApplication
from jdTextEdit.gui.CodeEdit import CodeEdit
from jdTextEdit.Settings import Settings
from typing import TYPE_CHECKING
from PyQt6.QtGui import QFont


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class StyleTab(QWidget, SettingsTabBase):
    def __init__(self, env: "Environment"):
        super().__init__()
        self.font = QFont()
        self.env = env

        self.themeSelect = QComboBox()
        self.foldSelect = QComboBox()
        self.fontCheckBox = QCheckBox(QCoreApplication.translate("StyleTab", "Font:"))
        self.fontButton = QPushButton()
        self.lineNumberCheckBox = QCheckBox(QCoreApplication.translate("StyleTab", "Show line numbers"))
        self.highlightLineCheckBox = QCheckBox(QCoreApplication.translate("StyleTab", "Highlight current line"))
        self.zoomSlider = QSlider(Qt.Orientation.Horizontal)
        self.editorPreview = CodeEdit(env, preview=True)

        for key, value in env.themes.items():
            self.themeSelect.addItem(value.getName(), key)

        self.foldSelect.addItem(QCoreApplication.translate("StyleTab", "None"))
        self.foldSelect.addItem(QCoreApplication.translate("StyleTab", "Plain"))
        self.foldSelect.addItem(QCoreApplication.translate("StyleTab", "Circled"))
        self.foldSelect.addItem(QCoreApplication.translate("StyleTab", "Boxed"))
        self.foldSelect.addItem(QCoreApplication.translate("StyleTab", "CircledTree"))
        self.foldSelect.addItem(QCoreApplication.translate("StyleTab", "BoxedTree"))

        self.zoomSlider.setMaximum(20)
        self.zoomSlider.setMinimum(-10)
        self.zoomSlider.setTickInterval(5)
        self.zoomSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
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
        for i in self.env.languageList:
            if i.getID() == "builtin.LUA":
                self.editorPreview.setLanguage(i)

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(QCoreApplication.translate("StyleTab", "Editor theme:")), 0, 0)
        gridLayout.addWidget(self.themeSelect, 0, 1)
        gridLayout.addWidget(QLabel(QCoreApplication.translate("StyleTab", "Fold style:")), 1, 0)
        gridLayout.addWidget(self.foldSelect, 1, 1)
        gridLayout.addWidget(self.fontCheckBox, 2, 0)
        gridLayout.addWidget(self.fontButton, 2, 1)

        zoomLayout = QHBoxLayout()
        zoomLayout.addWidget(QLabel(QCoreApplication.translate("StyleTab", "Default zoom:")))
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
        self.fontButton.setEnabled(self.fontCheckBox.isChecked())
        self.updatePreviewEdit()

    def fontButtonClicked(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.fontButton.setText(font.family())
            self.font = font
            self.updatePreviewEdit()

    def updatePreviewEdit(self):
        self.editorPreview.setSettings(self.getSettings(Settings(defaultSettings=self.env.defaultSettings)))

    def updateTab(self, settings: Settings):
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

    def getSettings(self, settings: Settings):
        settings.set("editTheme", self.themeSelect.itemData(self.themeSelect.currentIndex()))
        settings.set("editFoldStyle", self.foldSelect.currentIndex())
        settings.set("useCustomFont", self.fontCheckBox.isChecked())
        settings.set("editFont", self.font)
        settings.set("editShowLineNumbers", self.lineNumberCheckBox.isChecked())
        settings.set("highlightCurrentLine", self.highlightLineCheckBox.isChecked())
        settings.set("defaultZoom", self.zoomSlider.value())
        return settings

    def title(self) -> str:
        return QCoreApplication.translate("StyleTab", "Style")
