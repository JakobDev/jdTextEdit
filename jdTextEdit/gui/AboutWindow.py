from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLayout
from jdTextEdit.Functions import getThemeIcon, restoreWindowState
import webbrowser

class AboutWindow(QWidget):
    def __init__(self, env):
        super().__init__()
        text = QLabel("<center>" + (env.translate("aboutWindow.label.title") % env.version) + "<br><br>" + env.translate("aboutWindow.label.description") + "<br><br>" + env.translate("aboutWindow.label.license") + "<br><br>Copyright © 2019 JakobDev</center>")
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
        mainLayout.addWidget(text)
        mainLayout.addLayout(buttonLayout)
        mainLayout.setSizeConstraint(QLayout.SetFixedSize)

        self.setLayout(mainLayout)
        self.setWindowTitle(env.translate("aboutWindow.title"))
