from PyQt5.QtWidgets import QWidget, QLineEdit, QCheckBox, QLabel, QHBoxLayout, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt5.QtGui import QIntValidator

class BigFilesTab(QWidget,SettingsTabBase):
    def __init__(self,env):
        super().__init__()
        self.env = env

        self.enableBigFiles = QCheckBox(env.translate("settingsWindow.bigFiles.checkBox.enableBigFiles"))
        self.filesFromLabel = QLabel(env.translate("settingsWindow.bigFiles.label.filesFrom"))
        self.bytesEdit = QLineEdit()
        self.bytesLabel = QLabel(env.translate("settingsWindow.bigFiles.label.bytes"))
        self.disableHighlight = QCheckBox(env.translate("settingsWindow.bigFiles.checkBox.disableHighlight"))
        self.disableEncodingDetect =  QCheckBox(env.translate("settingsWindow.bigFiles.disableEncodingDetect"))
        self.showBanner = QCheckBox(env.translate("settingsWindow.bigFiles.showBanner"))

        self.enableBigFiles.stateChanged.connect(self.enableFilesChanged)
        self.bytesEdit.setValidator(QIntValidator(0,2147483647))

        self.pluginCheckBoxList = []
        for i in env.customBigFilesSettings:
            self.pluginCheckBoxList.append([QCheckBox(i[1]),i[0]])

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

    def enableFilesChanged(self):
        enabled = bool(self.enableBigFiles.checkState())
        self.filesFromLabel.setEnabled(enabled)
        self.bytesEdit.setEnabled(enabled)
        self.bytesLabel.setEnabled(enabled)
        self.disableHighlight.setEnabled(enabled)
        self.disableEncodingDetect.setEnabled(enabled)
        self.showBanner.setEnabled(enabled)
        for i in self.pluginCheckBoxList:
            i[0].setEnabled(enabled)

    def updateTab(self,settings):
        self.enableBigFiles.setChecked(settings.enableBigFileLimit)
        self.bytesEdit.setText(str(settings.bigFileSize))
        self.disableHighlight.setChecked(settings.bigFileDisableHighlight)
        self.disableEncodingDetect.setChecked(settings.bigFileDisableEncodingDetect)
        self.showBanner.setChecked(settings.bigFileShowBanner)
        self.enableFilesChanged()
        for i in self.pluginCheckBoxList:
            i[0].setChecked(settings.get(i[1]))

    def getSettings(self,settings):
        settings.enableBigFileLimit = bool(self.enableBigFiles.checkState())
        settings.bigFileSize = int(self.bytesEdit.text())
        settings.bigFileDisableHighlight = bool(self.disableHighlight.checkState())
        settings.bigFileDisableEncodingDetect  = bool(self.disableEncodingDetect.checkState())
        settings.bigFileShowBanner = bool(self.showBanner.checkState())

    def title(self):
        return self.env.translate("settingsWindow.bigFiles")
