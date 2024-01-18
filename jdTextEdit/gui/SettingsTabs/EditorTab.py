from PyQt6.QtWidgets import QWidget, QLabel, QCheckBox, QSpinBox, QComboBox, QGridLayout, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.EncodingList import getEncodingList
from PyQt6.QtCore import QCoreApplication
from jdTextEdit.Settings import Settings
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class EditorTab(QWidget, SettingsTabBase):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env

        self.defaultEncodingComboBox = QComboBox()
        self.defaultEolModeComboBox = QComboBox()
        self.defaultLanguageComboBox = QComboBox()
        self.tabWidthSpinBox = QSpinBox()
        self.tabSpaces = QCheckBox(QCoreApplication.translate("EditorTab", "Insert Spaces instead of Tabs"))
        self.textWrap = QCheckBox(QCoreApplication.translate("EditorTab", "Enable Text wrapping"))
        self.showWhitespaces = QCheckBox(QCoreApplication.translate("EditorTab", "Show Whitespaces"))
        self.autoIndent = QCheckBox(QCoreApplication.translate("EditorTab", "Automatic indentation"))
        self.showIndentationGuides = QCheckBox(QCoreApplication.translate("EditorTab", "Show indentation guides"))
        self.showEol = QCheckBox(QCoreApplication.translate("EditorTab", "Show end of line"))
        self._highlightOccurrencesSelectedText = QCheckBox(QCoreApplication.translate("EditorTab", "Highlight all occurrences of selected text"))

        for i in getEncodingList():
            self.defaultEncodingComboBox.addItem(i[0])

        self.defaultEolModeComboBox.addItem("Windows")
        self.defaultEolModeComboBox.addItem("Unix")
        self.defaultEolModeComboBox.addItem("Mac")

        self.defaultLanguageComboBox.addItem(QCoreApplication.translate("EditorTab", "Plain Text"), "plain")

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(QCoreApplication.translate("EditorTab", "Default encoding:")), 0, 0)
        gridLayout.addWidget(self.defaultEncodingComboBox, 0, 1)
        gridLayout.addWidget(QLabel(QCoreApplication.translate("EditorTab", "Default end of line:")), 1, 0)
        gridLayout.addWidget(self.defaultEolModeComboBox, 1, 1)
        gridLayout.addWidget(QLabel(QCoreApplication.translate("EditorTab", "Default language:")), 2, 0)
        gridLayout.addWidget(self.defaultLanguageComboBox, 2, 1)
        gridLayout.addWidget(QLabel(QCoreApplication.translate("EditorTab", "Default width:")), 3, 0)
        gridLayout.addWidget(self.tabWidthSpinBox, 3, 1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addWidget(self.tabSpaces)
        mainLayout.addWidget(self.textWrap)
        mainLayout.addWidget(self.showWhitespaces)
        mainLayout.addWidget(self.autoIndent)
        mainLayout.addWidget(self.showIndentationGuides)
        mainLayout.addWidget(self.showEol)
        mainLayout.addWidget(self._highlightOccurrencesSelectedText)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def updateTab(self, settings: Settings) -> None:
        for i in range(self.defaultEncodingComboBox.count()):
            if self.defaultEncodingComboBox.itemText(i) == settings.defaultEncoding:
                self.defaultEncodingComboBox.setCurrentIndex(i)

        self.defaultEolModeComboBox.setCurrentIndex(settings.defaultEolMode)

        pos = self.defaultLanguageComboBox.findData(settings.defaultLanguage)
        if pos == -1:
            self.defaultLanguageComboBox.setCurrentIndex(0)
        else:
            self.defaultLanguageComboBox.setCurrentIndex(pos)

        self.tabWidthSpinBox.setValue(settings.editTabWidth)
        self.tabSpaces.setChecked(settings.editTabSpaces)
        self.textWrap.setChecked(settings.editTextWrap)
        self.showWhitespaces.setChecked(settings.editShowWhitespaces)
        self.autoIndent.setChecked(settings.editAutoIndent)
        self.showIndentationGuides.setChecked(settings.showIndentationGuides)
        self.showEol.setChecked(settings.editShowEol)
        self._highlightOccurrencesSelectedText.setChecked(settings.get("editHighlightOccurrencesSelectedText"))

    def getSettings(self, settings: Settings) -> None:
        settings.set("defaultEncoding", self.defaultEncodingComboBox.currentText())
        settings.set("defaultEolMode", self.defaultEolModeComboBox.currentIndex())
        settings.set("defaultLanguage", self.defaultLanguageComboBox.currentData())
        settings.set("editTabWidth", self.tabWidthSpinBox.value())
        settings.set("editTabSpaces", self.tabSpaces.isChecked())
        settings.set("editTextWrap", self.textWrap.isChecked())
        settings.set("editShowWhitespaces", self.showWhitespaces.isChecked())
        settings.set("editAutoIndent", self.autoIndent.isChecked())
        settings.set("showIndentationGuides", self.showIndentationGuides.isChecked())
        settings.set("editShowEol", self.showEol.isChecked())
        settings.set("editHighlightOccurrencesSelectedText", self._highlightOccurrencesSelectedText.isChecked())

    def setup(self) -> None:
        for i in self.env.languageList:
            self.defaultLanguageComboBox.addItem(i.getName(), i.getID())

    def title(self) -> str:
        return QCoreApplication.translate("EditorTab", "Editor")
