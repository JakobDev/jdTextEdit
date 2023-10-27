from PyQt6.QtWidgets import QWidget, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QVBoxLayout
from jdTextEdit.Functions import showMessageBox, restoreWindowState, sortActionDict
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
from PyQt6.QtGui import QAction
import traceback
import sys


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class ActionSearchWindow(QWidget):
    def __init__(self, env: "Environment"):
        super().__init__()
        self._env = env
        self._actionList: list[QAction] = []

        self._searchBox = QLineEdit()
        self._resultList = QListWidget()
        self._okButton = QPushButton(QCoreApplication.translate("ActionSearchWindow", "OK"))
        cancelButton = QPushButton(QCoreApplication.translate("ActionSearchWindow", "Cancel"))

        self._searchBox.textChanged.connect(self._doSearch)
        self._resultList.itemClicked.connect(lambda: self._okButton.setEnabled(True))
        self._resultList.itemDoubleClicked.connect(self._runSelectedAction)
        self._okButton.clicked.connect(self._runSelectedAction)
        cancelButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        if env.settings.get("swapOkCancel"):
            buttonLayout.addWidget(self._okButton)
            buttonLayout.addWidget(cancelButton)
        else:
            buttonLayout.addWidget(cancelButton)
            buttonLayout.addWidget(self._okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self._searchBox)
        mainLayout.addWidget(self._resultList)
        mainLayout.addLayout(buttonLayout)

        self.setWindowTitle(QCoreApplication.translate("ActionSearchWindow", "Search Action"))
        self.setLayout(mainLayout)

        restoreWindowState(self, env.windowState, "ActionSearchWindow")

    def _doSearch(self):
        self._resultList.clear()
        self._actionList.clear()
        self._okButton.setEnabled(False)
        searchString = self._searchBox.text().lower()
        for key, value in sortActionDict(self._env.menuActions).items():
            if value.data()[0] == "separator":
                continue
            actionText = value.text().replace("&", "")
            if actionText.lower().find(searchString) != -1:
                item = QListWidgetItem(value.icon(), actionText)
                self._resultList.addItem(item)
                self._actionList.append(value)

    def _runSelectedAction(self):
        try:
            pos = self._resultList.currentRow()
            self._actionList[pos].triggered.emit()
            self.close()
        except Exception as ex:
            self._env.logger.exception(ex)
            showMessageBox(QCoreApplication.translate("ActionSearchWindow", "Unknown error"), QCoreApplication.translate("ActionSearchWindow", "An unknown error occured"))

    def openWindow(self):
        self._searchBox.setText("")
        self._searchBox.setFocus()
        self._doSearch()
        self.show()
