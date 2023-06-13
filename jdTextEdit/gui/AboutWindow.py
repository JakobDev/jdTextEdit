from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLayout
from PyQt6.QtCore import Qt, QCoreApplication
from jdTextEdit.Functions import getThemeIcon
from typing import TYPE_CHECKING
from PyQt6.QtGui import QIcon
import webbrowser
import os


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class AboutWindow(QWidget):
    def __init__(self, env: "Environment"):
        super().__init__()
        logo = QLabel()
        logo.setPixmap(QIcon(os.path.join(env.programDir, "Logo.svg")).pixmap(100, 100))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text = "<center>"
        text += QCoreApplication.translate("AboutWindow", "jdTextEdit version {{version}}").replace("{{version}}", env.version) + "<br><br>"
        text += QCoreApplication.translate("AboutWindow", "jdTextEdit is a feature rich text editor with plugin support") + "<br><br>"
        text += QCoreApplication.translate("AboutWindow", "This Program is licensed under GPL 3") + "<br><br>"
        text += QCoreApplication.translate("AboutWindow", "The logo was made by Axel-Erfurt") + "<br><br>"
        if "aboutMessage" in env.distributionSettings:
            text += env.distributionSettings["aboutMessage"] + "<br><br>"
        text += "Copyright © 2019-2023 JakobDev</center>"
        label = QLabel(text)
        viewSourceButton = QPushButton(QCoreApplication.translate("AboutWindow", "View Source"))
        closeButton = QPushButton(QCoreApplication.translate("AboutWindow", "Close"))

        viewSourceButton.setIcon(getThemeIcon(env, "applications-internet"))
        closeButton.setIcon(getThemeIcon(env, "window-close"))

        viewSourceButton.clicked.connect(lambda: webbrowser.open("https://codeberg.org/JakobDev/jdTextEdit"))
        closeButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(viewSourceButton)
        buttonLayout.addWidget(closeButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(logo)
        mainLayout.addWidget(label)
        mainLayout.addLayout(buttonLayout)
        mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(mainLayout)
        self.setWindowTitle(QCoreApplication.translate("AboutWindow", "About"))
