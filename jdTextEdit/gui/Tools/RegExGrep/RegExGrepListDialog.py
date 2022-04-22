from PyQt6.QtWidgets import  QDialog, QInputDialog, QMessageBox
from jdTextEdit.Functions import readJsonFile
from PyQt6.QtCore import QCoreApplication
from typing import Dict
from PyQt6 import uic
import json
import os


class RegExGrepListDialog(QDialog):
    def __init__(self, env, parentWindow):
        self.env = env
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "RegExGrepListDialog.ui"), self)

        self.env = env
        self.regExGrepWindow = parentWindow

        self._savedRegEx: Dict[str, str] = {}

        self.regExList.currentItemChanged.connect(self._updateButtonsEnabled)
        self.searchEdit.textChanged.connect(self._updateRegExList)

        self.loadButton.clicked.connect(self._loadButtonClicked)
        self.saveButton.clicked.connect(self._saveButtonClicked)
        self.removeButton.clicked.connect(self._removeButtonClicked)
        self.cancelButton.clicked.connect(self.close)

    def _updateButtonsEnabled(self):
        if self.regExList.currentItem() is None:
            self.loadButton.setEnabled(False)
            self.removeButton.setEnabled(False)
        else:
            self.loadButton.setEnabled(True)
            self.removeButton.setEnabled(True)

        if self.regExGrepWindow.regExEdit.text() == "":
            self.saveButton.setEnabled(False)
        else:
            self.saveButton.setEnabled(True)

    def _updateRegExList(self):
        self.regExList.clear()
        searchText = self.searchEdit.text().lower()
        for i in self._savedRegEx.keys():
            if i.lower().find(searchText) != -1:
                self.regExList.addItem(i)
        self._updateButtonsEnabled()

    def _loadButtonClicked(self):
        item = self.regExList.currentItem()
        self.regExGrepWindow.regExEdit.setText(self._savedRegEx[item.text()])
        self.close()

    def _saveButtonClicked(self):
        name, ok = QInputDialog.getText(self, QCoreApplication.translate("RegExGrepListDialog", "Enter name"), QCoreApplication.translate("RegExGrepListDialog", "Please enter a Name under which you want to save your RegEx"))

        if not ok:
            return

        if name in self._savedRegEx:
            QMessageBox.critical(self, QCoreApplication.translate("RegExGrepListDialog", "Already taken"), QCoreApplication.translate("RegExGrepListDialog", "This name has already been taken"))
            return

        self._savedRegEx[name] = self.regExGrepWindow.regExEdit.text()

        self._updateRegExList()

        with open(os.path.join(self.env.dataDir, "savedRegEx.json"), "w", encoding="utf-8") as f:
            json.dump(self._savedRegEx, f, ensure_ascii=False, indent=4)

    def _removeButtonClicked(self):
        if QMessageBox.question(self, QCoreApplication.translate("RegExGrepListDialog", "Remove RegEx"), QCoreApplication.translate("RegExGrepListDialog", "Are you sure you want to remove the selected RegEx?")) != QMessageBox.StandardButton.Yes:
            return

        item = self.regExList.currentItem()
        del self._savedRegEx[item.text()]
        self._updateRegExList()

        with open(os.path.join(self.env.dataDir, "savedRegEx.json"), "w", encoding="utf-8") as f:
            json.dump(self._savedRegEx, f, ensure_ascii=False, indent=4)

    def openWindow(self):
        self._savedRegEx = readJsonFile(os.path.join(self.env.dataDir, "savedRegEx.json"), {})
        self._updateRegExList()
        self.exec()
