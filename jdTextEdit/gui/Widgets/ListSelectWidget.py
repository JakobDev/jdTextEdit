from PyQt6.QtWidgets import QWidget, QPushButton, QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon
from typing import List
import copy


class CustomWidgetItem(QListWidgetItem):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.actionNameString = ""

    def setActionName(self, name: str) -> None:
        self.actionNameString = name

    def actionName(self) -> str:
        return self.actionNameString


class ListSelectWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.elements: List[List[str]] = []

        addButton = QPushButton(QCoreApplication.translate("ListSelectWidget", "Add"))
        removeButton = QPushButton(QCoreApplication.translate("ListSelectWidget", "Remove"))
        upButton = QPushButton(QCoreApplication.translate("ListSelectWidget", "Up"))
        downButton = QPushButton(QCoreApplication.translate("ListSelectWidget", "Down"))

        self.elementsListWidget = QListWidget()
        self.userListWidget = QListWidget()

        addButton.setIcon(QIcon.fromTheme("go-next"))
        removeButton.setIcon(QIcon.fromTheme("go-previous"))
        upButton.setIcon(QIcon.fromTheme("go-up"))
        downButton.setIcon(QIcon.fromTheme("go-down"))

        addButton.clicked.connect(self._addButtonClicked)
        removeButton.clicked.connect(self._removeButtonClicked)
        upButton.clicked.connect(self._upButtonClicked)
        downButton.clicked.connect(self._downButtonClicked)

        buttonLayout = QVBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(addButton)
        buttonLayout.addWidget(removeButton)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(upButton)
        buttonLayout.addWidget(downButton)
        buttonLayout.addStretch(1)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.elementsListWidget)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addWidget(self.userListWidget)

        self.setLayout(mainLayout)

    def _addButtonClicked(self):
        baseItem = self.elementsListWidget.currentItem()
        if not baseItem:
            return
        newItem = CustomWidgetItem(baseItem.text())
        newItem.setActionName(baseItem.actionName())
        self.userListWidget.addItem(newItem)

    def _removeButtonClicked(self):
        row = self.userListWidget.currentRow()
        self.userListWidget.takeItem(row)

    def _upButtonClicked(self):
        currentRow = self.userListWidget.currentRow()
        currentItem = self.userListWidget.takeItem(currentRow)
        self.userListWidget.insertItem(currentRow - 1, currentItem)
        self.userListWidget.setCurrentRow(currentRow - 1)

    def _downButtonClicked(self):
        currentRow = self.userListWidget.currentRow()
        currentItem = self.userListWidget.takeItem(currentRow)
        self.userListWidget.insertItem(currentRow + 1, currentItem)
        self.userListWidget.setCurrentRow(currentRow + 1)

    def setElements(self, elements: List[List[str]]):
        self.elements = copy.deepcopy(elements)
        self.elementsListWidget.clear()

        for i in self.elements:
            item = CustomWidgetItem(i[1])
            item.setActionName(i[0])
            self.elementsListWidget.addItem(item)

    def setSelectedIDList(self, id_list: List[str]):
        self.userListWidget.clear()
        for i in id_list:
            for elem in self.elements:
                if elem[0] == i:
                    item = CustomWidgetItem(elem[1])
                    item.setActionName(i)
                    self.userListWidget.addItem(item)
                    continue

    def getSelectedIDList(self) -> List[str]:
        id_list = []
        for i in range(self.userListWidget.count()):
            id_list.append(self.userListWidget.item(i).actionName())
        return id_list

    def clear(self):
        self.elementsListWidget.clear()
        self.userListWidget.clear()
        self.elements.clear()
