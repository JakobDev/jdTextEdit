from PyQt6.QtWidgets import QWidget, QPushButton, QListWidget, QHBoxLayout, QVBoxLayout, QListWidgetItem, QCheckBox, QComboBox, QLabel, QGridLayout
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


class ToolbarTab(QWidget, SettingsTabBase):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env

        self.actionsList = QListWidget()
        addButton = QPushButton(QCoreApplication.translate("ToolbarTab", "Add"))
        removeButton = QPushButton(QCoreApplication.translate("ToolbarTab", "Remove"))
        upButton = QPushButton(QCoreApplication.translate("ToolbarTab", "Move Up"))
        downButton = QPushButton(QCoreApplication.translate("ToolbarTab", "Move Down"))
        self.contextList = QListWidget()
        self.showToolbarCheckbox = QCheckBox(QCoreApplication.translate("ToolbarTab", "Show Toolbar"))
        self.iconStyleSelect = QComboBox()
        self.positionComboBox = QComboBox()

        self.iconStyleSelect.addItem(QCoreApplication.translate("ToolbarTab", "Icon only"))
        self.iconStyleSelect.addItem(QCoreApplication.translate("ToolbarTab", "Text only"))
        self.iconStyleSelect.addItem(QCoreApplication.translate("ToolbarTab", "Text beside Icons"))
        self.iconStyleSelect.addItem(QCoreApplication.translate("ToolbarTab", "Text under Icons"))
        self.iconStyleSelect.addItem(QCoreApplication.translate("ToolbarTab", "Follow OS Style"))

        self.positionComboBox.addItem(QCoreApplication.translate("ToolbarTab", "Up"))
        self.positionComboBox.addItem(QCoreApplication.translate("ToolbarTab", "Bottom"))
        self.positionComboBox.addItem(QCoreApplication.translate("ToolbarTab", "Left"))
        self.positionComboBox.addItem(QCoreApplication.translate("ToolbarTab", "Right"))

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

        menuLayout = QHBoxLayout()
        menuLayout.addWidget(self.actionsList)
        menuLayout.addLayout(buttonLayout)
        menuLayout.addWidget(self.contextList)

        optionsLayout = QGridLayout()
        optionsLayout.addWidget(QLabel(QCoreApplication.translate("ToolbarTab", "Toolbar button style:")), 0, 0)
        optionsLayout.addWidget(self.iconStyleSelect, 0, 1)
        optionsLayout.addWidget(QLabel(QCoreApplication.translate("ToolbarTab", "Position:")), 1, 0)
        optionsLayout.addWidget(self.positionComboBox, 1, 1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(menuLayout)
        mainLayout.addLayout(optionsLayout)
        mainLayout.addWidget(self.showToolbarCheckbox)

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
        for i in settings.toolBar:
            if i in self.env.menuActions:
                action = self.env.menuActions[i]
                item = CustomWidgetItem(action.text().removeprefix("&"))
            else:
                item = CustomWidgetItem(QCoreApplication.translate("ToolbarTab", "Unknown Action"))
            item.setActionName(i)
            self.contextList.addItem(item)
        self.showToolbarCheckbox.setChecked(settings.showToolbar)
        self.iconStyleSelect.setCurrentIndex(settings.toolbarIconStyle)
        self.positionComboBox.setCurrentIndex(settings.toolbarPosition)

    def getSettings(self, settings: Settings) -> None:
        settings.toolBar.clear()

        for i in range(self.contextList.count()):
            settings.toolBar.append(self.contextList.item(i).actionName())

        settings.set("showToolbar", self.showToolbarCheckbox.isChecked())
        settings.set("toolbarIconStyle", self.iconStyleSelect.currentIndex())
        settings.set("toolbarPosition", self.positionComboBox.currentIndex())

    def setup(self) -> None:
        for key, data in self.env.menuActions.items():
            item = CustomWidgetItem(data.text().removeprefix("&"))
            item.setActionName(data.data()[0])
            self.actionsList.addItem(item)
        self.actionsList.sortItems()

    def title(self) -> str:
        return QCoreApplication.translate("ToolbarTab", "Toolbar")
