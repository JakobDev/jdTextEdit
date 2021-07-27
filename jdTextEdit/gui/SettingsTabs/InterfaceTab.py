from PyQt6.QtWidgets import QWidget, QComboBox, QLabel, QCheckBox, QGridLayout, QVBoxLayout, QStyleFactory
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.Functions import selectComboBoxItem
from jdTextEdit.Settings import Settings

class InterfaceTab(QWidget,SettingsTabBase):
    def __init__(self,env):
        super().__init__()
        self.env = env

        self.styleSelectComboBox = QComboBox()
        self.settingsWindowType = QComboBox()
        self.swapOkCancel = QCheckBox(env.translate("settingsWindow.interface.checkBox.swapOkCancel"))
        self.enableUserChrome = QCheckBox(env.translate("settingsWindow.interface.checkBox.enableUserChrome"))

        self.styleSelectComboBox.addItem(env.translate("settingsWindow.interface.combobox.systemStyle"))
        self.styleSelectComboBox.addItems(QStyleFactory.keys())

        self.settingsWindowType.addItem(env.translate("settingsWindow.interface.combobox.modern"))
        self.settingsWindowType.addItem(env.translate("settingsWindow.interface.combobox.classic"))

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(env.translate("settingsWindow.interface.label.applicationStyle")), 0, 0)
        gridLayout.addWidget(self.styleSelectComboBox, 0, 1)
        gridLayout.addWidget(QLabel(env.translate("settingsWindow.interface.label.settingsDesign")),1,0)
        gridLayout.addWidget(self.settingsWindowType,1,1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addWidget(self.swapOkCancel)
        mainLayout.addWidget(self.enableUserChrome)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def updateTab(self, settings: Settings):
        applicationStyle = settings.get("applicationStyle")
        if applicationStyle == "default":
            self.styleSelectComboBox.setCurrentIndex(0)
        else:
            selectComboBoxItem(self.styleSelectComboBox,applicationStyle)
        if settings.get("settingsWindowUseModernDesign"):
            self.settingsWindowType.setCurrentIndex(0)
        else:
            self.settingsWindowType.setCurrentIndex(1)
        self.swapOkCancel.setChecked(settings.get("swapOkCancel"))
        self.enableUserChrome.setChecked(settings.get("enableUserChrome"))

    def getSettings(self, settings: Settings):
        if self.styleSelectComboBox.currentIndex() == 0:
            settings.set("applicationStyle","default")
        else:
            settings.applicationStyle = self.styleSelectComboBox.itemText(self.styleSelectComboBox.currentIndex())
        if self.settingsWindowType.currentIndex() == 0:
            settings.set("settingsWindowUseModernDesign",True)
        else:
            settings.set("settingsWindowUseModernDesign",False)
        settings.set("swapOkCancel", self.swapOkCancel.isChecked())
        settings.set("enableUserChrome",self.enableUserChrome.isChecked())

    def title(self) -> str:
        return self.env.translate("settingsWindow.interface")