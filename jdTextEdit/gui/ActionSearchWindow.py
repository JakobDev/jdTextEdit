from PyQt6.QtWidgets import QWidget, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QVBoxLayout
from jdTextEdit.Functions import showMessageBox, restoreWindowState
import traceback
import sys


class ActionSearchWindow(QWidget):
    def __init__(self, env):
        super().__init__()
        self._env = env
        self._actionList = []

        self._searchBox = QLineEdit()
        self._resultList = QListWidget()
        self._okButton = QPushButton(env.translate("button.ok"))
        cancelButton = QPushButton(env.translate("button.cancel"))

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

        self.setWindowTitle(env.translate("searchActionWindow.title"))
        self.setLayout(mainLayout)

        restoreWindowState(self, env.windowState, "ActionSearchWindow")

    def _doSearch(self):
        self._resultList.clear()
        self._actionList.clear()
        self._okButton.setEnabled(False)
        searchString = self._searchBox.text().lower()
        for key, value in self._env.menuActions.items():
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
        except:
            print(traceback.format_exc(), end="", file=sys.stderr)
            showMessageBox(self._env.translate("unknownError.title"), self._env.translate("unknownError.text"))

    def openWindow(self):
        self._searchBox.setText("")
        self._searchBox.setFocus()
        self._doSearch()
        self.show()
