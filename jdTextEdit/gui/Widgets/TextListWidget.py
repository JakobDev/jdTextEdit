from PyQt6.QtWidgets import QWidget, QListWidget, QPushButton, QInputDialog, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import QCoreApplication


class TextListWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self._listWidget = QListWidget()

        addButton = QPushButton(QCoreApplication.translate("TextListWidget", "Add"))
        self._editButton = QPushButton(QCoreApplication.translate("TextListWidget", "Edit"))
        self._removeButton = QPushButton(QCoreApplication.translate("TextListWidget", "Remove"))

        self._listWidget.itemSelectionChanged.connect(self._updateButtonsEnabled)
        addButton.clicked.connect(self._addButtonClicked)
        self._editButton.clicked.connect(self._editButtonClicked)
        self._removeButton.clicked.connect(self._removeButtonClicked)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(addButton)
        buttonLayout.addWidget(self._editButton)
        buttonLayout.addWidget(self._removeButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self._listWidget)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def _addButtonClicked(self) -> None:
        text = QInputDialog.getText(self, QCoreApplication.translate("TextListWidget", "New Item"), QCoreApplication.translate("TextListWidget", "Please enter a text"))[0]

        if text == "":
            return

        self._listWidget.addItem(text)
        self._updateButtonsEnabled()

    def _editButtonClicked(self) -> None:
        item = self._listWidget.currentItem()
        text = QInputDialog.getText(self, QCoreApplication.translate("TextListWidget", "Edit Item"), QCoreApplication.translate("TextListWidget", "Please edit a text"), text=item.text())[0]

        if text == "":
            return

        item.setText(text)
        self._updateButtonsEnabled()

    def _removeButtonClicked(self) -> None:
        self._listWidget.takeItem(self._listWidget.currentRow())
        self._updateButtonsEnabled()

    def _updateButtonsEnabled(self) -> None:
        enabled = self._listWidget.currentRow() != -1
        self._editButton.setEnabled(enabled)
        self._removeButton.setEnabled(enabled)

    def setTextList(self, textList: list[str]) -> None:
        self._listWidget.clear()
        self._listWidget.addItems(textList)
        self._updateButtonsEnabled()

    def getTextList(self) -> list[str]:
        textList: list[str] = []
        for i in range(self._listWidget.count()):
            textList.append(self._listWidget.item(i).text())
        return textList
