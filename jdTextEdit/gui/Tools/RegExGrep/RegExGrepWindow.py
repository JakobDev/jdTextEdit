from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from .RegExGrepListDialog import RegExGrepListDialog
from jdTextEdit.Functions import isRegExValid
from PyQt6.QtCore import QCoreApplication
from PyQt6 import uic
import os
import re


class RegExGrepWindow(QWidget):
    def __init__(self, env):
        self.env = env
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "RegExGrepWindow.ui"), self)

        self._savedRegExDialog = RegExGrepListDialog(env, self)

        self.savedRegExButton.clicked.connect(self._savedRegExDialog.openWindow)
        self.copyButton.clicked.connect(self._copyButtonClicked)
        self.okButton.clicked.connect(self._okButtonClicked)
        self.cancelButton.clicked.connect(self.close)

    def _copyButtonClicked(self):
        if self.resultsList.count() == 0:
            QMessageBox.information(self, QCoreApplication.translate("RegExGrepWindow", "No results"), QCoreApplication.translate("RegExGrepWindow", "There are no results to copy"))
            return

        text = ""
        for i in range(self.resultsList.count()):
            text += self.resultsList.item(i).text() + "\n"
        QApplication.clipboard().setText(text)

        QMessageBox.information(self, QCoreApplication.translate("RegExGrepWindow", "Data copied"), QCoreApplication.translate("RegExGrepWindow", "The content of the results List has been copied into your clipboard"))

    def _okButtonClicked(self):
        if self.regExEdit.text() == "":
            QMessageBox.information(self, QCoreApplication.translate("RegExGrepWindow", "No RegEx"), QCoreApplication.translate("RegExGrepWindow", "You have not entered a RegEx"))
            return

        if not isRegExValid(self.regExEdit.text()):
            QMessageBox.critical(self, QCoreApplication.translate("RegExGrepWindow", "Invalid RegEx"), QCoreApplication.translate("RegExGrepWindow", "Your RegEx is invalid"))
            return

        self.resultsList.clear()
        for i in re.findall(self.regExEdit.text(), self.env.mainWindow.getTextEditWidget().text()):
            self.resultsList.addItem(i)

        if self.resultsList.count() == 0:
            QMessageBox.information(self, QCoreApplication.translate("RegExGrepWindow", "Nothing found"), QCoreApplication.translate("RegExGrepWindow", "The given RegEx haven't found anything"))
