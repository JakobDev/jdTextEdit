from PyQt6.QtWidgets import QWidget, QCheckBox, QComboBox, QLabel, QHBoxLayout, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.Functions import selectComboBoxItem
from jdTextEdit.Settings import Settings

class OpenTab(QWidget,SettingsTabBase):
    def __init__(self, env):
        super().__init__()
        self.env = env

        self.useIPCCheckBox = QCheckBox(env.translate("settingsWindow.open.checkBox.useIPC"))
        self.detectLanguage = QCheckBox(env.translate("settingsWindow.open.checkBox.detectLanguage"))
        self.detectEol = QCheckBox(env.translate("settingsWindow.open.checkBox.detectEol"))
        self.detectEncoding = QCheckBox(env.translate("settingsWindow.open.checkBox.detectEncoding"))
        self.encodingBannerCheckBox = QCheckBox(env.translate("settingsWindow.open.checkBox.showEncodingBanner"))
        self.eolBannerCheckBox = QCheckBox(env.translate("settingsWindow.open.checkBox.showEolBanner"))
        self.detectLibComboBox = QComboBox()

        for key, value in env.encodingDetectFunctions.items():
            self.detectLibComboBox.addItem(key)

        detectLibLayout = QHBoxLayout()
        detectLibLayout.addWidget(QLabel(env.translate("settingsWindow.open.label.encodingDetectLib")))
        detectLibLayout.addWidget(self.detectLibComboBox)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.useIPCCheckBox)
        mainLayout.addWidget(self.detectLanguage)
        mainLayout.addWidget(self.detectEol)
        mainLayout.addWidget(self.detectEncoding)
        mainLayout.addWidget(self.encodingBannerCheckBox)
        mainLayout.addWidget(self.eolBannerCheckBox)
        mainLayout.addLayout(detectLibLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def updateTab(self, settings: Settings):
        self.useIPCCheckBox.setChecked(settings.useIPC)
        self.detectLanguage.setChecked(settings.detectLanguage)
        self.detectEol.setChecked(settings.detectEol)
        self.detectEncoding.setChecked(settings.detectEncoding)
        self.encodingBannerCheckBox.setChecked(settings.showEncodingBanner)
        self.eolBannerCheckBox.setChecked(settings.showEolBanner)
        selectComboBoxItem(self.detectLibComboBox,settings.encodingDetectLib)

    def getSettings(self, settings: Settings):
        settings.set("useIPC",self.useIPCCheckBox.isChecked())
        settings.set("detectLanguage",self.detectLanguage.isChecked())
        settings.set("detectEncoding",self.detectEncoding.isChecked())
        settings.set("detectEol",self.detectEol.isChecked())
        settings.set("showEncodingBanner",self.encodingBannerCheckBox.isChecked())
        settings.set("showEolBanner",self.eolBannerCheckBox.isChecked())
        settings.set("encodingDetectLib",self.detectLibComboBox.itemText(self.detectLibComboBox.currentIndex()))

    def title(self) -> str:
        return self.env.translate("settingsWindow.open")
