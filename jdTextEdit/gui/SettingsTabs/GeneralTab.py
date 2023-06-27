from PyQt6.QtWidgets import QWidget, QComboBox, QLabel, QCheckBox, QGridLayout, QVBoxLayout, QSpinBox
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.Languages import getLanguageNames
from PyQt6.QtCore import QCoreApplication
from jdTextEdit.Settings import Settings
from typing import TYPE_CHECKING
import os


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class GeneralTab(QWidget, SettingsTabBase):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env

        self.languageComboBox = QComboBox()
        self.recentFilesSpinBox = QSpinBox()
        self.saveCloseCheckBox = QCheckBox(QCoreApplication.translate("GeneralTab", "Ask for save, when trying to close a edited file"))
        self.saveSessionCheckBox = QCheckBox(QCoreApplication.translate("GeneralTab", "Save Session"))
        self.pluginsCheckBox = QCheckBox(QCoreApplication.translate("GeneralTab", "Load Plugins"))
        self.nativeIconsCheckBox = QCheckBox(QCoreApplication.translate("GeneralTab", "Use native Icons"))
        self.dayTipCheckBox = QCheckBox(QCoreApplication.translate("GeneralTab", "Show tip of the day on startup"))
        self.windowTitleCheckBox = QCheckBox(QCoreApplication.translate("GeneralTab", "Show filename in window title"))
        self.searchUpdatesCheckBox = QCheckBox(QCoreApplication.translate("GeneralTab", "Check for updates at startup"))
        self.windowStateCheckBox = QCheckBox(QCoreApplication.translate("GeneralTab", "Save window status"))
        self.fileChangedBannerCheckBox = QCheckBox(QCoreApplication.translate("GeneralTab", "Monitor open files for changes"))

        self.languageComboBox.addItem(QCoreApplication.translate("GeneralTab", "Use system default"), "default")

        count = 1
        languageNames = getLanguageNames()
        languageList = os.listdir(os.path.join(env.programDir, "translations"))
        self.languageComboBox.addItem(languageNames["en"], "en")
        for i in languageList:
            if not i.endswith(".qm"):
                continue

            language = i.removeprefix("jdTextEdit_").removesuffix(".qm")
            self.languageComboBox.addItem(languageNames.get(language, language), language)
            count += 1

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(QCoreApplication.translate("GeneralTab", "Language (needs restart):")), 0, 0)
        gridLayout.addWidget(self.languageComboBox, 0, 1)
        gridLayout.addWidget(QLabel(QCoreApplication.translate("GeneralTab", "Length of recent files list")), 1, 0)
        gridLayout.addWidget(self.recentFilesSpinBox, 1, 1)

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

    def updateTab(self, settings: Settings) -> None:
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

    def getSettings(self, settings: Settings) -> None:
        settings.set("language", self.languageComboBox.itemData(self.languageComboBox.currentIndex()))
        settings.set("maxRecentFiles", self.recentFilesSpinBox.value())
        settings.set("saveClose", self.saveCloseCheckBox.isChecked())
        settings.set("saveSession", self.saveSessionCheckBox.isChecked())
        settings.set("loadPlugins", self.pluginsCheckBox.isChecked())
        settings.set("useNativeIcons", self.nativeIconsCheckBox.isChecked())
        settings.set("startupDayTip", self.dayTipCheckBox.isChecked())
        settings.set("windowFileTitle", self.windowTitleCheckBox.isChecked())
        settings.set("searchUpdates", self.searchUpdatesCheckBox.isChecked())
        settings.set("saveWindowState", self.windowStateCheckBox.isChecked())
        settings.set("showFileChangedBanner", self.fileChangedBannerCheckBox.isChecked())

    def title(self) -> str:
        return QCoreApplication.translate("GeneralTab", "General")
