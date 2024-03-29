from PyQt6.QtWidgets import QWidget, QLineEdit, QCheckBox, QLabel, QHBoxLayout, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt6.QtCore import QCoreApplication
from jdTextEdit.Settings import Settings
from PyQt6.QtGui import QIntValidator
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class BigFilesTab(QWidget, SettingsTabBase):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env

        self.enableBigFiles = QCheckBox(QCoreApplication.translate("BigFilesTab", "Limit big files"))
        self.filesFromLabel = QLabel(QCoreApplication.translate("BigFilesTab", "Files from"))
        self.bytesEdit = QLineEdit()
        self.bytesLabel = QLabel(QCoreApplication.translate("BigFilesTab", "bytes"))
        self.disableHighlight = QCheckBox(QCoreApplication.translate("BigFilesTab", "Disable syntax highlighting"))
        self.disableEncodingDetect = QCheckBox(QCoreApplication.translate("BigFilesTab", "Disable encoding detect"))
        self.showBanner = QCheckBox(QCoreApplication.translate("BigFilesTab", "Show banner"))

        self.enableBigFiles.stateChanged.connect(self.enableFilesChanged)
        self.bytesEdit.setValidator(QIntValidator(0, 2147483647))

        self.pluginCheckBoxList = []
        for i in env.customBigFilesSettings:
            self.pluginCheckBoxList.append([QCheckBox(i[1]), i[0]])

        editLayout = QHBoxLayout()
        editLayout.addWidget(self.filesFromLabel)
        editLayout.addWidget(self.bytesEdit)
        editLayout.addWidget(self.bytesLabel)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.enableBigFiles)
        mainLayout.addLayout(editLayout)
        mainLayout.addWidget(self.disableHighlight)
        mainLayout.addWidget(self.disableEncodingDetect)
        for i in self.pluginCheckBoxList:
            mainLayout.addWidget(i[0])
        mainLayout.addWidget(self.showBanner)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def enableFilesChanged(self) -> None:
        enabled = self.enableBigFiles.isChecked()
        self.filesFromLabel.setEnabled(enabled)
        self.bytesEdit.setEnabled(enabled)
        self.bytesLabel.setEnabled(enabled)
        self.disableHighlight.setEnabled(enabled)
        self.disableEncodingDetect.setEnabled(enabled)
        self.showBanner.setEnabled(enabled)
        for i in self.pluginCheckBoxList:
            i[0].setEnabled(enabled)

    def updateTab(self, settings: Settings) -> None:
        self.enableBigFiles.setChecked(settings.enableBigFileLimit)
        self.bytesEdit.setText(str(settings.bigFileSize))
        self.disableHighlight.setChecked(settings.bigFileDisableHighlight)
        self.disableEncodingDetect.setChecked(settings.bigFileDisableEncodingDetect)
        self.showBanner.setChecked(settings.bigFileShowBanner)
        self.enableFilesChanged()
        for i in self.pluginCheckBoxList:
            i[0].setChecked(settings.get(i[1]))

    def getSettings(self, settings: Settings) -> None:
        settings.set("enableBigFileLimit", self.enableBigFiles.isChecked())
        settings.set("bigFileSize", int(self.bytesEdit.text()))
        settings.set("bigFileDisableHighlight", self.disableHighlight.isChecked())
        settings.set("bigFileDisableEncodingDetect", self.disableEncodingDetect.isChecked())
        settings.set("bigFileShowBanner", self.showBanner.isChecked())

    def title(self) -> str:
        return QCoreApplication.translate("BigFilesTab", "Big Files")
