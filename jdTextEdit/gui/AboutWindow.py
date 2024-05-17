from PyQt6.QtWidgets import QWidget, QLabel, QTextBrowser, QPushButton, QTabWidget, QVBoxLayout
from jdTextEdit.Functions import getThemeIcon, readJsonFile
from jdTextEdit.Languages import getLanguageNames
from PyQt6.QtCore import Qt, QCoreApplication
from typing import TYPE_CHECKING
from PyQt6.QtGui import QIcon
import os


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class AboutTab(QWidget):
    def __init__(self, env: "Environment") -> None:
        super().__init__()

        text = "<center>"
        text += QCoreApplication.translate("AboutWindow", "jdTextEdit is a feature rich text editor with plugin support") + "<br><br>"
        text += QCoreApplication.translate("AboutWindow", "This Program is licensed under GPL 3") + "<br><br>"
        text += QCoreApplication.translate("AboutWindow", "The logo was made by Axel-Erfurt") + "<br><br>"
        if "aboutMessage" in env.distributionSettings:
            text += env.distributionSettings["aboutMessage"] + "<br><br>"
        text += "Copyright © 2019-2024 JakobDev</center>"

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel(text))
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)


class TranslatorsTab(QWidget):
    def __init__(self, env: "Environment") -> None:
        super().__init__()

        translatorsView = QTextBrowser()
        translatorsText = ""
        languageNames = getLanguageNames()
        for language, translators in readJsonFile(os.path.join(env.programDir, "data", "translators.json"), {}).items():
            translatorsText += f"<b>{languageNames.get(language, language)}</b><br>\n"
            for translatorName in translators:
                translatorsText += f"{translatorName}<br>\n"
            translatorsText += "<br>\n"

        if translatorsText == "":
            translatorsView.setText(QCoreApplication.translate("AboutWindow", "Error: translators.json was not found"))
        else:
            translatorsText = translatorsText.removesuffix("<br>\n")
            translatorsView.setHtml(translatorsText)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("<center>" + QCoreApplication.translate("AboutWindow", "The following people translated jdTextEdit:") + "</center>"))
        mainLayout.addWidget(translatorsView)

        self.setLayout(mainLayout)


class ChangelogTab(QWidget):
    def __init__(self, env: "Environment") -> None:
        super().__init__()

        changelogView = QTextBrowser()

        with open(os.path.join(env.programDir, "data", "changelog.html"), "r", encoding="utf-8") as f:
            changelogView.setHtml(f.read())

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(changelogView)

        self.setLayout(mainLayout)


class AboutWindow(QWidget):
    def __init__(self, env: "Environment") -> None:
        super().__init__()

        logo = QLabel()
        logo.setPixmap(QIcon(os.path.join(env.programDir, "Logo.svg")).pixmap(64, 64))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        closeButton = QPushButton(QCoreApplication.translate("AboutWindow", "Close"))

        tabWidget = QTabWidget()
        tabWidget.addTab(AboutTab(env), QCoreApplication.translate("AboutWindow", "About"))
        tabWidget.addTab(TranslatorsTab(env), QCoreApplication.translate("AboutWindow", "Translators"))
        tabWidget.addTab(ChangelogTab(env), QCoreApplication.translate("AboutWindow", "Changelog"))

        closeButton.setIcon(getThemeIcon(env, "window-close"))

        closeButton.clicked.connect(self.close)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(logo)
        mainLayout.addWidget(QLabel("<center>" + QCoreApplication.translate("AboutWindow", "jdTextEdit version {{version}}").replace("{{version}}", env.version) + "<center>"))
        mainLayout.addWidget(tabWidget)
        mainLayout.addWidget(closeButton)

        self.setLayout(mainLayout)
        self.setWindowTitle(QCoreApplication.translate("AboutWindow", "About"))

        self.resize(mainLayout.minimumSize())
