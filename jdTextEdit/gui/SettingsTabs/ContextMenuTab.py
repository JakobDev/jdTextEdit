from PyQt6.QtWidgets import QWidget, QPushButton, QListWidget, QHBoxLayout, QVBoxLayout, QListWidgetItem
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt6.QtCore import QCoreApplication
from jdTextEdit.Settings import Settings
from typing import TYPE_CHECKING
from PyQt6.QtGui import QIcon


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class CustomWidgetItem(QListWidgetItem):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.actionNameString = ""

    def setActionName(self, name: str) -> None:
        self.actionNameString = name

    def actionName(self) -> str:
        return self.actionNameString


class ContextMenuTab(QWidget, SettingsTabBase):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env
        self.actionsList = QListWidget()
        addButton = QPushButton(QCoreApplication.translate("ContextMenuTab", "Add"))
        removeButton = QPushButton(QCoreApplication.translate("ContextMenuTab", "Remove"))
        upButton = QPushButton(QCoreApplication.translate("ContextMenuTab", "Move Up"))
        downButton = QPushButton(QCoreApplication.translate("ContextMenuTab", "Move Down"))
        self.contextList = QListWidget()

        addButton.setIcon(QIcon.fromTheme("go-next"))
        removeButton.setIcon(QIcon.fromTheme("go-previous"))
        upButton.setIcon(QIcon.fromTheme("go-up"))
        downButton.setIcon(QIcon.fromTheme("go-down"))

        addButton.clicked.connect(self.addButtonClicked)
        removeButton.clicked.connect(self.removeButtonClicked)
        upButton.clicked.connect(self.upButtonClicked)
        downButton.clicked.connect(self.downButtonClicked)

        buttonLayout = QVBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(addButton)
        buttonLayout.addWidget(removeButton)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(upButton)
        buttonLayout.addWidget(downButton)
        buttonLayout.addStretch(1)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.actionsList)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addWidget(self.contextList)

        self.setLayout(mainLayout)

    def addButtonClicked(self) -> None:
        item = self.actionsList.currentItem()
        if item:
            if item.actionName() != "separator":
                for i in range(self.contextList.count()):
                    if self.contextList.item(i).actionName() == item.actionName():
                        return
            newItem = CustomWidgetItem(item.text())
            newItem.setActionName(item.actionName())
            self.contextList.addItem(newItem)

    def removeButtonClicked(self) -> None:
        row = self.contextList.currentRow()
        self.contextList.takeItem(row)

    def upButtonClicked(self) -> None:
        currentRow = self.contextList.currentRow()
        currentItem = self.contextList.takeItem(currentRow)
        self.contextList.insertItem(currentRow - 1, currentItem)
        self.contextList.setCurrentRow(currentRow - 1)

    def downButtonClicked(self) -> None:
        currentRow = self.contextList.currentRow()
        currentItem = self.contextList.takeItem(currentRow)
        self.contextList.insertItem(currentRow + 1, currentItem)
        self.contextList.setCurrentRow(currentRow + 1)

    def updateTab(self, settings: Settings) -> None:
        self.contextList.clear()
        for i in settings.editContextMenu:
            if i in self.env.menuActions:
                action = self.env.menuActions[i]
                item = CustomWidgetItem(action.text().removeprefix("&"))
            else:
                item = CustomWidgetItem(QCoreApplication.translate("ContextMenuTab", "Unknown Action"))
            item.setActionName(i)
            self.contextList.addItem(item)

    def getSettings(self, settings: Settings) -> None:
        settings.editContextMenu = []
        for i in range(self.contextList.count()):
            settings.editContextMenu.append(self.contextList.item(i).actionName())

    def setup(self) -> None:
        for key, data in self.env.menuActions.items():
            if data.text().startswith("&"):
                item = CustomWidgetItem(data.text()[1:])
            else:
                item = CustomWidgetItem(data.text())
            item.setActionName(data.data()[0])
            self.actionsList.addItem(item)
            self.actionsList.sortItems()

    def title(self) -> str:
        return QCoreApplication.translate("ContextMenuTab", "Context menu")
