from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLayout
from jdTextEdit.Functions import getThemeIcon, restoreWindowState
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import webbrowser
import os

class AboutWindow(QWidget):
    def __init__(self, env):
        super().__init__()
        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join(env.programDir,"Logo.png")).scaled(100,100))
        logo.setAlignment(Qt.AlignCenter)
        text = "<center>"
        text += (env.translate("aboutWindow.label.title") % env.version) + "<br><br>"
        text += env.translate("aboutWindow.label.description") + "<br><br>"
        text +=  env.translate("aboutWindow.label.license") + "<br><br>"
        text += env.translate("aboutWindow.label.logoAuthor") + "<br><br>"
        if "aboutMessage" in env.distributionSettings:
            text += env.distributionSettings["aboutMessage"] +  "<br><br>"
        text += "Copyright © 2019-2021 JakobDev</center>"
        label = QLabel(text)
        #label = QLabel("<center>" + (env.translate("aboutWindow.label.title") % env.version) + "<br><br>" + env.translate("aboutWindow.label.description") + "<br><br>"+ env.translate("aboutWindow.label.license") + "<br><br>"  + env.translate("aboutWindow.label.logoAuthor") + "<br><br>Copyright © 2019-2021 JakobDev</center>")
        viewSourceButton = QPushButton(env.translate("aboutWindow.button.viewSource"))
        closeButton = QPushButton(env.translate("button.close"))

        viewSourceButton.setIcon(getThemeIcon(env,"applications-internet"))
        closeButton.setIcon(getThemeIcon(env,"window-close"))

        viewSourceButton.clicked.connect(lambda: webbrowser.open("https://gitlab.com/JakobDev/jdTextEdit"))
        closeButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(viewSourceButton)
        buttonLayout.addWidget(closeButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(logo)
        mainLayout.addWidget(label)
        mainLayout.addLayout(buttonLayout)
        mainLayout.setSizeConstraint(QLayout.SetFixedSize)

        self.setLayout(mainLayout)
        self.setWindowTitle(env.translate("aboutWindow.title"))
