from PyQt6.QtWidgets import QLabel, QWidget, QCheckBox, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt6.QtCore import  QCoreApplication
from jdTextEdit.Settings import Settings
from typing import TYPE_CHECKING

try:
    import editorconfig
except ModuleNotFoundError:
    pass


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class EditorconfigTab(QWidget, SettingsTabBase):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env

        editorconfigNotFoundLabel = QLabel(QCoreApplication.translate("EditorconfigTab", "The editorconfig module was not found"))
        editorconfigNotFoundLabel.setStyleSheet("""
            border-radius: 1px;
            border-style: solid;
            border-width: 1px;
            border-color: darkred;
            background: orangered;
            color: black;
            font-weight: bold;
        """)

        self.useEditorConfig = QCheckBox(QCoreApplication.translate("EditorconfigTab", "Use .editorconfig if available"))
        self.useIndentStyle = QCheckBox(QCoreApplication.translate("EditorconfigTab", "Use indentation style from .editorconfig"))
        self.tabWidth = QCheckBox(QCoreApplication.translate("EditorconfigTab", "Use tab width from .editorconfig"))
        self.endOfLine = QCheckBox(QCoreApplication.translate("EditorconfigTab", "Use end of line from .editorconfig"))
        self.trimWhitespace = QCheckBox(QCoreApplication.translate("EditorconfigTab", "Use setting to trim whitespaces from .editorconfig"))
        self.insertNewline = QCheckBox(QCoreApplication.translate("EditorconfigTab", "Use setting to insert end of line from .editorconfig"))
        self.showBanner = QCheckBox(QCoreApplication.translate("EditorconfigTab", "Show notice when .editorconfig is used"))

        self.useEditorConfig.stateChanged.connect(self.toogleCheckBoxEnabled)

        mainLayout = QVBoxLayout()

        try:
            editorconfig
        except NameError:
            mainLayout.addWidget(editorconfigNotFoundLabel)
            self.useEditorConfig.setEnabled(False)

        mainLayout.addWidget(self.useEditorConfig)
        mainLayout.addWidget(self.useIndentStyle)
        mainLayout.addWidget(self.tabWidth)
        mainLayout.addWidget(self.endOfLine)
        mainLayout.addWidget(self.trimWhitespace)
        mainLayout.addWidget(self.insertNewline)
        mainLayout.addWidget(self.showBanner)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def toogleCheckBoxEnabled(self) -> None:
        try:
            editorconfig
            enabled = self.useEditorConfig.isChecked()
        except NameError:
            enabled = False
        self.useIndentStyle.setEnabled(enabled)
        self.tabWidth.setEnabled(enabled)
        self.endOfLine.setEnabled(enabled)
        self.trimWhitespace.setEnabled(enabled)
        self.insertNewline.setEnabled(enabled)
        self.showBanner.setEnabled(enabled)

    def updateTab(self, settings: Settings) -> None:
        self.useEditorConfig.setChecked(settings.useEditorConfig)
        self.useIndentStyle.setChecked(settings.editorConfigUseIndentStyle)
        self.tabWidth.setChecked(settings.editorConfigTabWidth)
        self.endOfLine.setChecked(settings.editorConfigEndOfLine)
        self.trimWhitespace.setChecked(settings.editorConfigTrimWhitespace)
        self.insertNewline.setChecked(settings.editorConfigInsertNewline)
        self.showBanner.setChecked(settings.editorConfigShowBanner)
        self.toogleCheckBoxEnabled()

    def getSettings(self, settings: Settings) -> None:
        settings.set("useEditorConfig", self.useEditorConfig.isChecked())
        settings.set("editorConfigUseIndentStyle", self.useIndentStyle.isChecked())
        settings.set("editorConfigTabWidth", self.tabWidth.isChecked())
        settings.set("editorConfigEndOfLine", self.endOfLine.isChecked())
        settings.set("editorConfigTrimWhitespace", self.trimWhitespace.isChecked())
        settings.set("editorConfigInsertNewline", self.insertNewline.isChecked())
        settings.set("editorConfigShowBanner", self.showBanner.isChecked())

    def title(self) -> str:
        return QCoreApplication.translate("EditorconfigTab", "Editorconfig")
