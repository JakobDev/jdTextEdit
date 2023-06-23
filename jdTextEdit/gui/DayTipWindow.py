from PyQt6.QtWidgets import QApplication, QWidget, QTextBrowser, QPushButton, QCheckBox, QHBoxLayout, QVBoxLayout
from jdTextEdit.Functions import restoreWindowState
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QCloseEvent
from typing import TYPE_CHECKING
import random


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class DayTipWindow(QWidget):
    def __init__(self, env: "Environment"):
        super().__init__()
        self.env = env

        self.textArea = QTextBrowser()
        self.showStartup = QCheckBox(QCoreApplication.translate("DayTipWindow", "Show tips on startup"))
        nextTipButton = QPushButton(QCoreApplication.translate("DayTipWindow", "Next tip"))
        closeButton = QPushButton(QCoreApplication.translate("DayTipWindow", "Close"))

        nextTipButton.clicked.connect(self.nextTip)
        closeButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(nextTipButton)
        buttonLayout.addWidget(closeButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.textArea)
        mainLayout.addWidget(self.showStartup)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(QCoreApplication.translate("DayTipWindow", "Tip of the day"))
        restoreWindowState(self, self.env.windowState, "DayTipWindow")

    def setup(self):
        self.tips = [
            QCoreApplication.translate("TipOfTheDay", "You can install plugins by putting them into the plugins directory in the data directory."),
            QCoreApplication.translate("TipOfTheDay", "jdTextEdit is available in multiple languages. You can change the language in the preferences."),
            QCoreApplication.translate("TipOfTheDay", "You can open the data directory in the about menu."),
            QCoreApplication.translate("TipOfTheDay", "You can change the syntax highlighter in the language menu."),
            QCoreApplication.translate("TipOfTheDay", "You can edit the Context menu and the toolbar in the preferences."),
            QCoreApplication.translate("TipOfTheDay", "You can add your own templates to the templates menu by putting them into the templates folder in the data directory."),
            QCoreApplication.translate("TipOfTheDay", "Don't like the default shortcuts? You can edit all shortcuts in the \"Shortcuts\" tab of the \"Preferences\" window."),
            QCoreApplication.translate("TipOfTheDay", "jdTextEdit has a sidebar with a lot of features! You can enabled it in the \"View\" menu."),
            QCoreApplication.translate("TipOfTheDay", "Start jdTextEdit with -p to use it in portable mode."),
            QCoreApplication.translate("TipOfTheDay", "You can use bookmarks to quickly jump to important points in the code."),
            QCoreApplication.translate("TipOfTheDay", "By clicking on the border you can set or remove bookmarks."),
            QCoreApplication.translate("TipOfTheDay", "jdTextEdit automatically checks for updates at startup. You can disable this in the settings. Alternatively you can use the about menu to check for updates."),
            QCoreApplication.translate("TipOfTheDay", "If you would like to redesign jdTextEdit with your own CSS code, you can create the file userChrome.css in the data directory. You can disable this in the settings."),
            QCoreApplication.translate("TipOfTheDay", "jdTextEdit automatically saves your session, so next time you can continue where you left off. You can disable this behavior in the preferences."),
            QCoreApplication.translate("TipOfTheDay", "jdTextEdit automatically detects language, line end and encoding of text files. You can disable this in the settings."),
            QCoreApplication.translate("TipOfTheDay", "jdTextEdit supports different line ends. The line end of the file is automatically recognized unless you have disabled it in the settings. You can change the line end of the current file in the edit menu. You can also change the settings to show the end of line."),
            QCoreApplication.translate("TipOfTheDay", "You can display the current clipboard content in the sidebar."),
            QCoreApplication.translate("TipOfTheDay", "You can set the data folder using the JDTEXTEDIT_DATA_PATH environment variable."),
            QCoreApplication.translate("TipOfTheDay", "If the directory \"default_data\" is located in the installation folder, it will be used when creating a new storage directory. You can use this to set preferences for multiple computers."),
            QCoreApplication.translate("TipOfTheDay", "You can open files by dragging and dropping them into the window."),
            QCoreApplication.translate("TipOfTheDay", "jdTextEdit supports the .editorconfig standard."),
            QCoreApplication.translate("TipOfTheDay", "Read the documentation of jdTextEdit at https://jdtextedit.readthedocs.io"),
            QCoreApplication.translate("TipOfTheDay", "Did you know that jdTextEdit runs on Linux, Windows macOS and Haiku?"),
        ]

        for key,value in self.env.translations.getStrings().items():
            if key.startswith("dayTip."):
                self.tips.append(value)
        self.selectedTip = None

    def nextTip(self):
        tip = random.randint(0, len(self.tips)-1)
        if tip == self.selectedTip:
            self.nextTip()
        else:
            self.textArea.setHtml(self.tips[tip])
            self.selectedTip = tip

    def openWindow(self):
        self.showStartup.setChecked(self.env.settings.startupDayTip)
        self.nextTip()
        self.show()
        QApplication.setActiveWindow(self)

    def closeEvent(self, event: QCloseEvent):
        self.env.settings.set("startupDayTip", self.showStartup.isChecked())
        event.accept()
