from PyQt6.QtWidgets import QWidget, QComboBox, QLabel, QCheckBox, QGridLayout, QVBoxLayout, QSpinBox, QStyleFactory
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.Settings import Settings
import os

class GeneralTab(QWidget,SettingsTabBase):
    def __init__(self,env):
        super().__init__()
        self.env = env

        self.languageComboBox = QComboBox()
        self.recentFilesSpinBox = QSpinBox()
        self.saveCloseCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.saveClose"))
        self.saveSessionCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.saveSession"))
        self.pluginsCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.loadPlugins"))
        self.nativeIconsCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.useNativeIcons"))
        self.dayTipCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.dayTip"))
        self.windowTitleCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.windowFileTitle"))
        self.searchUpdatesCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.searchUpdates"))
        self.windowStateCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.saveWindowState"))
        self.fileChangedBannerCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.showFileChangedBanner"))
        self.languageComboBox.addItem(env.translate("settingsWindow.general.combobox.systemDefault"))
        self.languageComboBox.setItemData(0,"default")

        count = 1
        languageList = os.listdir(os.path.join(env.programDir,"translation"))
        for i in languageList:
            language = i[:-5]
            self.languageComboBox.addItem(env.translate("language." + language))
            self.languageComboBox.setItemData(count,language)
            count +=1

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(env.translate("settingsWindow.general.label.languageSelect")),0,0)
        gridLayout.addWidget(self.languageComboBox,0,1)
        gridLayout.addWidget(QLabel(env.translate("settingsWindow.general.label.maxRecentFiles")),1,0)
        gridLayout.addWidget(self.recentFilesSpinBox,1,1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addWidget(self.saveCloseCheckBox)
        mainLayout.addWidget(self.saveSessionCheckBox)
        mainLayout.addWidget(self.pluginsCheckBox)
        mainLayout.addWidget(self.nativeIconsCheckBox)
        mainLayout.addWidget(self.dayTipCheckBox)
        mainLayout.addWidget(self.windowTitleCheckBox)
        if env.enableUpdater:
            mainLayout.addWidget(self.searchUpdatesCheckBox)
        mainLayout.addWidget(self.windowStateCheckBox)
        mainLayout.addWidget(self.fileChangedBannerCheckBox)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def updateTab(self, settings: Settings):
        for i in range(self.languageComboBox.count()):
            if self.languageComboBox.itemData(i) == settings.language:
                self.languageComboBox.setCurrentIndex(i)
        self.recentFilesSpinBox.setValue(settings.maxRecentFiles)
        self.saveCloseCheckBox.setChecked(settings.saveClose)
        self.saveSessionCheckBox.setChecked(settings.saveSession)
        self.pluginsCheckBox.setChecked(settings.loadPlugins)
        self.nativeIconsCheckBox.setChecked(settings.useNativeIcons)
        self.dayTipCheckBox.setChecked(settings.startupDayTip)
        self.windowTitleCheckBox.setChecked(settings.windowFileTitle)
        self.searchUpdatesCheckBox.setChecked(settings.searchUpdates)
        self.windowStateCheckBox.setChecked(settings.saveWindowState)
        self.fileChangedBannerCheckBox.setChecked(settings.showFileChangedBanner)

    def getSettings(self, settings: Settings):
        settings.set("language",self.languageComboBox.itemData(self.languageComboBox.currentIndex()))
        settings.set("maxRecentFiles",self.recentFilesSpinBox.value())
        settings.set("saveClose",self.saveCloseCheckBox.isChecked())
        settings.set("saveSession",self.saveSessionCheckBox.isChecked())
        settings.set("loadPlugins",self.pluginsCheckBox.isChecked())
        settings.set("useNativeIcons",self.nativeIconsCheckBox.isChecked())
        settings.set("startupDayTip",self.dayTipCheckBox.isChecked())
        settings.set("windowFileTitle",self.windowTitleCheckBox.isChecked())
        settings.set("searchUpdates",self.searchUpdatesCheckBox.isChecked())
        settings.set("saveWindowState",self.windowStateCheckBox.isChecked())
        settings.set("showFileChangedBanner",self.fileChangedBannerCheckBox.isChecked())

    def title(self) -> str:
        return self.env.translate("settingsWindow.general")
