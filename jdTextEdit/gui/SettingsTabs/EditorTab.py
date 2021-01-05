from PyQt5.QtWidgets import QWidget, QLabel, QCheckBox, QSpinBox, QComboBox, QGridLayout, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.EncodingList import getEncodingList

class EditorTab(QWidget,SettingsTabBase):
    def __init__(self,env):
        super().__init__()
        self.env = env

        self.defaultEncodingComboBox = QComboBox()
        self.defaultEolModeComboBox = QComboBox()
        self.defaultLanguageComboBox = QComboBox()
        self.tabWidthSpinBox = QSpinBox()
        self.tabSpaces = QCheckBox(env.translate("settingsWindow.editor.checkBox.editTabSpaces"))
        self.textWrap = QCheckBox(env.translate("settingsWindow.editor.checkBox.textWrap"))
        self.showWhitespaces = QCheckBox(env.translate("settingsWindow.editor.checkBox.showWhitespaces"))
        self.autoIndent = QCheckBox(env.translate("settingsWindow.editor.checkBox.autoIndent"))
        self.showIndentationGuides = QCheckBox(env.translate("settingsWindow.editor.checkBox.showIndentationGuides"))
        self.showEol = QCheckBox(env.translate("settingsWindow.editor.checkBox.showEol"))

        for i in getEncodingList():
            self.defaultEncodingComboBox.addItem(i[0])

        self.defaultEolModeComboBox.addItem("Windows")
        self.defaultEolModeComboBox.addItem("Unix")
        self.defaultEolModeComboBox.addItem("Mac")

        self.defaultLanguageComboBox.addItem(env.translate("mainWindow.menu.language.plainText"),"plain")

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(env.translate("settingsWindow.editor.label.defaultEncoding")),0,0)
        gridLayout.addWidget(self.defaultEncodingComboBox,0,1)
        gridLayout.addWidget(QLabel(env.translate("settingsWindow.editor.label.defaultEolMode")),1,0)
        gridLayout.addWidget(self.defaultEolModeComboBox,1,1)
        gridLayout.addWidget(QLabel(env.translate("settingsWindow.editor.label.defaultLanguage")),2,0)
        gridLayout.addWidget(self.defaultLanguageComboBox,2,1)
        gridLayout.addWidget(QLabel(env.translate("settingsWindow.editor.label.tabWidth")),3,0)
        gridLayout.addWidget(self.tabWidthSpinBox,3,1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addWidget(self.tabSpaces)
        mainLayout.addWidget(self.textWrap)
        mainLayout.addWidget(self.showWhitespaces)
        mainLayout.addWidget(self.autoIndent)
        mainLayout.addWidget(self.showIndentationGuides)
        mainLayout.addWidget(self.showEol)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def updateTab(self, settings):
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


    def getSettings(self, settings):
        settings.defaultEncoding = self.defaultEncodingComboBox.currentText()
        settings.defaultEolMode = self.defaultEolModeComboBox.currentIndex()
        settings.defaultLanguage = self.defaultLanguageComboBox.currentData()
        settings.editTabWidth = self.tabWidthSpinBox.value()
        settings.editTabSpaces = bool(self.tabSpaces.checkState())
        settings.editTextWrap = bool(self.textWrap.checkState())
        settings.editShowWhitespaces = bool(self.showWhitespaces.checkState())
        settings.editAutoIndent = bool(self.autoIndent.checkState())
        settings.showIndentationGuides = bool(self.showIndentationGuides.checkState())
        settings.editShowEol = bool(self.showEol.checkState())

    def setup(self):
        for i in self.env.languageList:
            self.defaultLanguageComboBox.addItem(i.getName(),i.getID())

    def title(self):
        return self.env.translate("settingsWindow.editor")
