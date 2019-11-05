from PyQt5.QtWidgets import QApplication, QWidget, QTextBrowser, QPushButton, QCheckBox, QHBoxLayout, QVBoxLayout
from jdTextEdit.Functions import restoreWindowState
import random
import os

class DayTipWindow(QWidget):
    def __init__(self,env):
        super().__init__()
        self.env = env
        
        self.textArea =  QTextBrowser()
        self.showStartup = QCheckBox(env.translate("dayTipWindow.showStartup"))
        nextTipButton = QPushButton(env.translate("dayTipWindow.nextTip"))
        closeButton = QPushButton(env.translate("button.close"))

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
        self.setWindowTitle(env.translate("dayTipWindow.title"))
        restoreWindowState(self,self.env.windowState,"DayTipWindow")

    def setup(self):
        self.tips = []
        for key,value in self.env.translations.strings.items():
            if key.startswith("dayTip."):
                self.tips.append(value)
        self.selectedTip = None

    def nextTip(self):
        tip = random.randint(0,len(self.tips)-1)
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

    def closeEvent(self, event):
        self.env.settings.startupDayTip = bool(self.showStartup.checkState())
        event.accept()
