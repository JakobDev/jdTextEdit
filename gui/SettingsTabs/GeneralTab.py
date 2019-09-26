from PyQt5.QtWidgets import QWidget, QComboBox, QLabel, QCheckBox, QGridLayout, QVBoxLayout, QSpinBox
import os

class GeneralTab(QWidget):
    def __init__(self,env):
        super().__init__()
        self.languageComboBox = QComboBox()
        self.recentFilesSpinBox = QSpinBox()
        self.saveCloseCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.saveClose"))
        self.hideTabBarCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.hideTabBar"))
        self.saveSessionCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.saveSession"))
        self.pluginsCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.loadPlugins"))
        self.nativeIconsCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.useNativeIcons"))
        self.toolbarCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.showToolbar"))
        self.dayTipCheckBox = QCheckBox(env.translate("settingsWindow.general.checkBox.dayTip"))
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
        mainLayout.addWidget(self.hideTabBarCheckBox)
        mainLayout.addWidget(self.saveSessionCheckBox)
        mainLayout.addWidget(self.pluginsCheckBox)
        mainLayout.addWidget(self.nativeIconsCheckBox)
        mainLayout.addWidget(self.toolbarCheckBox)
        mainLayout.addWidget(self.dayTipCheckBox)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def updateTab(self, settings):
        for i in range(self.languageComboBox.count()):
            if self.languageComboBox.itemData(i) == settings.language:
                self.languageComboBox.setCurrentIndex(i)
        self.recentFilesSpinBox.setValue(settings.maxRecentFiles)
        self.saveCloseCheckBox.setChecked(settings.saveClose)
        self.hideTabBarCheckBox.setChecked(settings.hideTabBar)
        self.saveSessionCheckBox.setChecked(settings.saveSession)
        self.pluginsCheckBox.setChecked(settings.loadPlugins)
        self.nativeIconsCheckBox.setChecked(settings.useNativeIcons)
        self.toolbarCheckBox.setChecked(settings.showToolbar)
        self.dayTipCheckBox.setChecked(settings.startupDayTip)

    def getSettings(self, settings):
        settings.language = self.languageComboBox.itemData(self.languageComboBox.currentIndex())
        settings.maxRecentFiles = self.recentFilesSpinBox.value()
        settings.saveClose = bool(self.saveCloseCheckBox.checkState())
        settings.hideTabBar = bool(self.hideTabBarCheckBox.checkState())
        settings.saveSession = bool(self.saveSessionCheckBox.checkState())
        settings.loadPlugins = bool(self.pluginsCheckBox.checkState())
        settings.useNativeIcons = bool(self.nativeIconsCheckBox.checkState())
        settings.showToolbar = bool(self.toolbarCheckBox.checkState())
        settings.startupDayTip = bool(self.dayTipCheckBox.checkState())
        return settings
