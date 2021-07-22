from PyQt6.QtWidgets import QWidget, QCheckBox, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.Settings import Settings


class EditorconfigTab(QWidget, SettingsTabBase):
    def __init__(self, env):
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
        enabled = self.useEditorConfig.isChecked()
        self.useIndentStyle.setEnabled(enabled)
        self.tabWidth.setEnabled(enabled)
        self.endOfLine.setEnabled(enabled)
        self.trimWhitespace.setEnabled(enabled)
        self.insertNewline.setEnabled(enabled)
        self.showBanner.setEnabled(enabled)

    def updateTab(self, settings: Settings):
        self.useEditorConfig.setChecked(settings.useEditorConfig)
        self.useIndentStyle.setChecked(settings.editorConfigUseIndentStyle)
        self.tabWidth.setChecked(settings.editorConfigTabWidth)
        self.endOfLine.setChecked(settings.editorConfigEndOfLine)
        self.trimWhitespace.setChecked(settings.editorConfigTrimWhitespace)
        self.insertNewline.setChecked(settings.editorConfigInsertNewline)
        self.showBanner.setChecked(settings.editorConfigShowBanner)
        self.toogleCheckBoxEnabled()

    def getSettings(self, settings: Settings):
        settings.set("useEditorConfig",self.useEditorConfig.isChecked())
        settings.set("editorConfigUseIndentStyle",self.useIndentStyle.isChecked())
        settings.set("editorConfigTabWidth",self.tabWidth.isChecked())
        settings.set("editorConfigEndOfLine",self.endOfLine.isChecked())
        settings.set("editorConfigTrimWhitespace",self.trimWhitespace.isChecked())
        settings.set("editorConfigInsertNewline",self.insertNewline.isChecked())
        settings.set("editorConfigShowBanner",self.showBanner.isChecked())

    def title(self) -> str:
        return self.env.translate("settingsWindow.editorconfig")
