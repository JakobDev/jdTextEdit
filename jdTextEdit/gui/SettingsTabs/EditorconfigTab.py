from PyQt5.QtWidgets import QWidget, QCheckBox, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase

class EditorconfigTab(QWidget,SettingsTabBase):
    def __init__(self,env):
        super().__init__()
        self.env = env

        self.useEditorConfig = QCheckBox(env.translate("settingsWindow.editorconfig.checkBox.useEditorConfig"))
        self.useIndentStyle = QCheckBox(env.translate("settingsWindow.editorconfig.checkBox.useIndentStyle"))
        self.tabWidth = QCheckBox(env.translate("settingsWindow.editorconfig.checkBox.tabWidth"))
        self.endOfLine = QCheckBox(env.translate("settingsWindow.editorconfig.checkBox.endOfLine"))
        self.trimWhitespace = QCheckBox(env.translate("settingsWindow.editorconfig.checkBox.trimWhitespace"))
        self.insertNewline = QCheckBox(env.translate("settingsWindow.editorconfig.checkBox.insertNewline"))
        self.showBanner = QCheckBox(env.translate("settingsWindow.editorconfig.checkBox.showBanner"))

        self.useEditorConfig.stateChanged.connect(self.toogleCheckBoxEnabled)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.useEditorConfig)
        mainLayout.addWidget(self.useIndentStyle)
        mainLayout.addWidget(self.tabWidth)
        mainLayout.addWidget(self.endOfLine)
        mainLayout.addWidget(self.trimWhitespace)
        mainLayout.addWidget(self.insertNewline)
        mainLayout.addWidget(self.showBanner)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def toogleCheckBoxEnabled(self):
        enabled =  bool(self.useEditorConfig.checkState())
        self.useIndentStyle.setEnabled(enabled)
        self.tabWidth.setEnabled(enabled)
        self.endOfLine.setEnabled(enabled)
        self.trimWhitespace.setEnabled(enabled)
        self.insertNewline.setEnabled(enabled)
        self.showBanner.setEnabled(enabled)

    def updateTab(self,settings):
        self.useEditorConfig.setChecked(settings.useEditorConfig)
        self.useIndentStyle.setChecked(settings.editorConfigUseIndentStyle)
        self.tabWidth.setChecked(settings.editorConfigTabWidth)
        self.endOfLine.setChecked(settings.editorConfigEndOfLine)
        self.trimWhitespace.setChecked(settings.editorConfigTrimWhitespace)
        self.insertNewline.setChecked(settings.editorConfigInsertNewline)
        self.showBanner.setChecked(settings.editorConfigShowBanner)
        self.toogleCheckBoxEnabled()

    def getSettings(self,settings):
         settings.useEditorConfig = bool(self.useEditorConfig.checkState())
         settings.editorConfigUseIndentStyle = bool(self.useIndentStyle.checkState())
         settings.editorConfigTabWidth = bool(self.tabWidth.checkState())
         settings.editorConfigEndOfLine = bool(self.endOfLine.checkState())
         settings.editorConfigTrimWhitespace = bool(self.trimWhitespace.checkState())
         settings.editorConfigInsertNewline = bool(self.insertNewline.checkState())
         settings.editorConfigShowBanner = bool(self.showBanner.checkState())

    def title(self):
        return self.env.translate("settingsWindow.editorconfig")
