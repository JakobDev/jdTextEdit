from PyQt5.QtWidgets import QWidget, QPushButton, QListWidget, QHBoxLayout, QVBoxLayout, QListWidgetItem, QCheckBox, QComboBox, QLabel, QGridLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt5.QtGui import QIcon

class CustomWidgetItem(QListWidgetItem):
    def __init__(self,name):
        super().__init__(name)
        self.actionNameString = ""

    def setActionName(self, name):
        self.actionNameString = name

    def actionName(self):
        return self.actionNameString

class ToolbarTab(QWidget,SettingsTabBase):
    def __init__(self,env):
        super().__init__()
        self.env = env

        self.actionsList = QListWidget()
        addButton = QPushButton(env.translate("settingsWindow.contextMenu.button.add"))
        removeButton = QPushButton(env.translate("settingsWindow.contextMenu.button.remove"))
        upButton = QPushButton(env.translate("settingsWindow.contextMenu.button.up"))
        downButton = QPushButton(env.translate("settingsWindow.contextMenu.button.down"))
        self.contextList = QListWidget()
        self.showToolbarCheckbox = QCheckBox(env.translate("settingsWindow.toolbar.checkBox.showToolbar"))
        self.iconStyleSelect = QComboBox()
        self.positionComboBox = QComboBox()

        self.iconStyleSelect.addItem(env.translate("settingsWindow.toolbar.buttonStyle.iconOnly"))
        self.iconStyleSelect.addItem(env.translate("settingsWindow.toolbar.buttonStyle.textOnly"))
        self.iconStyleSelect.addItem(env.translate("settingsWindow.toolbar.buttonStyle.textBesideIcons"))
        self.iconStyleSelect.addItem(env.translate("settingsWindow.toolbar.buttonStyle.textUnderIcons"))
        self.iconStyleSelect.addItem(env.translate("settingsWindow.toolbar.buttonStyle.osStyle"))

        self.positionComboBox.addItem(env.translate("position.up"))
        self.positionComboBox.addItem(env.translate("position.bottom"))
        self.positionComboBox.addItem(env.translate("position.left"))
        self.positionComboBox.addItem(env.translate("position.right"))

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
        optionsLayout.addWidget(QLabel(env.translate("settingsWindow.toolbar.label.buttonStyle")),0,0)
        optionsLayout.addWidget(self.iconStyleSelect,0,1)
        optionsLayout.addWidget(QLabel(env.translate("settingsWindow.toolbar.label.position")),1,0)
        optionsLayout.addWidget(self.positionComboBox,1,1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(menuLayout)
        mainLayout.addLayout(optionsLayout)
        mainLayout.addWidget(self.showToolbarCheckbox)

        self.setLayout(mainLayout)

    def addButtonClicked(self):
        item = self.actionsList.currentItem()
        if item:
            if item.actionName() != "separator":
                for i in range(self.contextList.count()):
                    if self.contextList.item(i).actionName() == item.actionName():
                        return
            newItem = CustomWidgetItem(item.text())
            newItem.setActionName(item.actionName())
            self.contextList.addItem(newItem)

    def removeButtonClicked(self):
        row = self.contextList.currentRow()
        self.contextList.takeItem(row)

    def upButtonClicked(self):
        currentRow = self.contextList.currentRow()
        currentItem = self.contextList.takeItem(currentRow)
        self.contextList.insertItem(currentRow - 1, currentItem)
        self.contextList.setCurrentRow(currentRow - 1)

    def downButtonClicked(self):
        currentRow = self.contextList.currentRow()
        currentItem = self.contextList.takeItem(currentRow)
        self.contextList.insertItem(currentRow + 1, currentItem)
        self.contextList.setCurrentRow(currentRow + 1)

    def updateTab(self, settings):
        self.contextList.clear()
        for i in settings.toolBar:
            if i in self.env.menuActions:
                action = self.env.menuActions[i]
                if action.text().startswith("&"):
                    item = CustomWidgetItem(action.text()[1:])
                else:
                    item = CustomWidgetItem(action.text())
            else:
                item = CustomWidgetItem(self.env.translate("settingsWindow.contextMenu.unknownAction"))
            item.setActionName(i)
            self.contextList.addItem(item)
        self.showToolbarCheckbox.setChecked(settings.showToolbar)
        self.iconStyleSelect.setCurrentIndex(settings.toolbarIconStyle)
        self.positionComboBox.setCurrentIndex(settings.toolbarPosition)

    def getSettings(self, settings):
        settings.toolBar = []
        for i in range(self.contextList.count()):
            settings.toolBar.append(self.contextList.item(i).actionName())
        settings.showToolbar = bool(self.showToolbarCheckbox.checkState())
        settings.toolbarIconStyle = self.iconStyleSelect.currentIndex()
        settings.toolbarPosition = self.positionComboBox.currentIndex()

    def setup(self):
        for key, data in self.env.menuActions.items():
            if data.text().startswith("&"):
                item = CustomWidgetItem(data.text()[1:])
            else:
                item = CustomWidgetItem(data.text())
            item.setActionName(data.data()[0])
            self.actionsList.addItem(item)

    def title(self):
        return self.env.translate("settingsWindow.toolbar")
