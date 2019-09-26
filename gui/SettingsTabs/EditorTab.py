from PyQt5.QtWidgets import QWidget, QLabel, QCheckBox, QSpinBox, QHBoxLayout, QVBoxLayout

class EditorTab(QWidget):
    def __init__(self,env):
        super().__init__()
        self.tabWidthSpinBox = QSpinBox()
        self.tabSpaces = QCheckBox(env.translate("settingsWindow.editor.checkBox.editTabSpaces"))
        self.textWrap = QCheckBox(env.translate("settingsWindow.editor.checkBox.textWrap"))
        self.showWhitespaces = QCheckBox(env.translate("settingsWindow.editor.checkBox.showWhitespaces"))
        self.autoIndent = QCheckBox(env.translate("settingsWindow.editor.checkBox.autoIndent"))
        self.showEol = QCheckBox(env.translate("settingsWindow.editor.checkBox.showEol"))

        tabWidthLayout = QHBoxLayout()
        tabWidthLayout.addWidget(QLabel(env.translate("settingsWindow.editor.label.tabWidth")))
        tabWidthLayout.addWidget(self.tabWidthSpinBox)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(tabWidthLayout)
        mainLayout.addWidget(self.tabSpaces)
        mainLayout.addWidget(self.textWrap)
        mainLayout.addWidget(self.showWhitespaces)
        mainLayout.addWidget(self.autoIndent)
        mainLayout.addWidget(self.showEol)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def updateTab(self, settings):
        self.tabWidthSpinBox.setValue(settings.editTabWidth)
        self.tabSpaces.setChecked(settings.editTabSpaces)
        self.textWrap.setChecked(settings.editTextWrap)
        self.showWhitespaces.setChecked(settings.editShowWhitespaces)
        self.autoIndent.setChecked(settings.editAutoIndent)
        self.showEol.setChecked(settings.editShowEol)

    def getSettings(self, settings):
        settings.editTabWidth = self.tabWidthSpinBox.value()
        settings.editTabSpaces = bool(self.tabSpaces.checkState())
        settings.editTextWrap = bool(self.textWrap.checkState())
        settings.editShowWhitespaces = bool(self.showWhitespaces.checkState())
        settings.editAutoIndent = bool(self.autoIndent.checkState())
        settings.editShowEol = bool(self.showEol.checkState())
        return settings
