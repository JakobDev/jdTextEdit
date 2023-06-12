from PyQt6.QtWidgets import QDialog, QListWidgetItem, QInputDialog, QMessageBox, QFileDialog
from jdTextEdit.gui.Windows.ManageThemesWindow.EditThemeWindow import EditThemeWindow
from jdTextEdit.Functions import readJsonFile
from typing import Optional, TYPE_CHECKING
from PyQt6.QtCore import QCoreApplication
from PyQt6 import uic
import json
import copy
import os


if TYPE_CHECKING:
    from jdTextEdit.gui.Windows.ManageThemesWindow.FileThemeDictType import FileThemeDict
    from jdTextEdit.Environment import Environment


class ManageThemeListWindow(QDialog):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self._env = env

        uic.loadUi(os.path.join(os.path.dirname(__file__), "ManageThemeListWindow.ui"), self)

        self._themeDict: dict[str, tuple["FileThemeDict", bool, Optional[str]]] = {}

        self._loadThemeDir(os.path.join(env.programDir, "themes"), True)
        self._loadThemeDir(os.path.join(env.dataDir, "themes"), False)
        self.updateListWidget()

        self.themeListWidget.itemSelectionChanged.connect(self._updateButtonsEnabled)
        self.newButton.clicked.connect(lambda: EditThemeWindow(self._env, self, None, None).exec())
        self.editButton.clicked.connect(lambda: EditThemeWindow(self._env, self, self._themeDict[self.themeListWidget.currentItem().data(42)][0], self._themeDict[self.themeListWidget.currentItem().data(42)][2]).exec())
        self.copyButton.clicked.connect(self._copyButtonCLicked)
        self.deleteButton.clicked.connect(self._deleteButtonClicked)
        self.importButton.clicked.connect(self._importButtonClicked)
        self.exportButton.clicked.connect(self._exportButtonClicked)
        self.closeButton.clicked.connect(self.close)

    def _loadThemeDir(self, dirPath: str, systemDir: bool) -> None:
        if not os.path.isdir(dirPath):
            return

        for i in os.listdir(dirPath):
            if not i.endswith(".json"):
                continue

            themeData = readJsonFile(os.path.join(dirPath, i), None)
            if themeData is not None:
                self.updateTheme(themeData, systemTheme=systemDir, filename=i)

    def _getCurrentTuple(self) -> Optional[tuple["FileThemeDict", bool, Optional[str]]]:
        try:
            return self._themeDict[self.themeListWidget.currentItem().data(42)]
        except (AttributeError, KeyError):
            return None

    def _copyButtonCLicked(self) -> None:
        currentTheme = self._getCurrentTuple()[0]

        name = QInputDialog.getText(self, QCoreApplication.translate("ManageThemeListWindow", "Enter name"), QCoreApplication.translate("ManageThemeListWindow", "Please enter a name"))[0]

        if name == "":
            return

        if self.doNameExists(name):
            QMessageBox.critical(self,  QCoreApplication.translate("ManageThemeListWindow", "Name exists"), QCoreApplication.translate("ManageThemeListWindow", "This name already exists"))
            return

        newTheme = copy.deepcopy(currentTheme)
        newTheme["id"] = self.generateThemeID(name)
        newTheme["name"] = name

        filename = self.getFreeFilename(newTheme["id"])

        self.updateTheme(newTheme, filename=filename)
        self.updateListWidget()

        with open(os.path.join(self._env.dataDir, "themes", filename), "w", encoding="utf-8") as f:
            json.dump(newTheme, f, ensure_ascii=False, indent=4)

    def _deleteButtonClicked(self) -> None:
        currentTuple = self._getCurrentTuple()

        if QMessageBox.question(self, QCoreApplication.translate("ManageThemeListWindow", "Delete {{name}}").replace("{{name}}", currentTuple[0]["name"]), QCoreApplication.translate("ManageThemeListWindow", "Are you sure you want to delete {{name}}?").replace("{{name}}", currentTuple[0]["name"]), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return

        del self._themeDict[currentTuple[0]["id"]]
        self.updateListWidget()

        os.remove(os.path.join(self._env.dataDir, "themes", currentTuple[2]))

    def _importButtonClicked(self) -> None:
        jsonFilterText = QCoreApplication.translate("ManageThemeListWindow", "JSON Files")
        allFilterText = QCoreApplication.translate("ManageThemeListWindow", "All Files")

        path = QFileDialog.getOpenFileName(self, filter=f"{jsonFilterText} (*.json);;{allFilterText} (*)")[0]

        if path == "":
            return

        themeData = readJsonFile(path, None)

        try:
            assert themeData is not None
            assert isinstance(themeData["id"], str)
            assert isinstance(themeData["name"], str)
            assert "global" not in themeData or isinstance(themeData["global"], dict)
            assert "lexer" not in themeData or isinstance(themeData["lexer"], dict)
        except AssertionError:
            QMessageBox.critical(self, QCoreApplication.translate("ManageThemeListWindow", "Invalid file"), QCoreApplication.translate("ManageThemeListWindow", "This file is not a valid theme"))
            return

    def _exportButtonClicked(self) -> None:
        currentTheme = self._getCurrentTuple()[0]

        jsonFilterText = QCoreApplication.translate("ManageThemeListWindow", "JSON Files")
        allFilterText = QCoreApplication.translate("ManageThemeListWindow", "All Files")

        path = QFileDialog.getSaveFileName(self, filter=f"{jsonFilterText} (*.json);;{allFilterText} (*)", directory=currentTheme["name"] + ".json")[0]

        if path == "":
            return

        with open(path, "w", encoding="utf-8") as f:
            json.dump(currentTheme, f, ensure_ascii=False, indent=4)

    def _updateButtonsEnabled(self) -> None:
        itemSelected = self.themeListWidget.currentRow() != -1

        if currentTuple := self._getCurrentTuple():
            systemTheme = currentTuple[1]
        else:
            systemTheme = False

        self.editButton.setEnabled(itemSelected and not systemTheme)
        self.copyButton.setEnabled(itemSelected)
        self.deleteButton.setEnabled(itemSelected and not systemTheme)
        self.exportButton.setEnabled(itemSelected)

    def updateTheme(self, theme: "FileThemeDict", systemTheme: bool = False, filename: Optional[str] = None) -> None:
        self._themeDict[theme["id"]] = (theme, systemTheme, filename)

    def updateListWidget(self) -> None:
        self.themeListWidget.clear()
        for i in self._themeDict.values():
            item = QListWidgetItem()
            item.setText(i[0]["name"])
            item.setData(42, i[0]["id"])
            self.themeListWidget.addItem(item)
        self._updateButtonsEnabled()

    def generateThemeID(self, name: str) -> str:
        if f"custom.{name}" not in self._themeDict:
            return f"custom.{name}"

        count = 1
        while True:
            currentID = f"custom.{name}{count}"
            if currentID not in self._themeDict:
                return currentID
            else:
                count += 1

    def getFreeFilename(self, themeID: str) -> str:
        themeID = themeID.removeprefix("custom.")
        currentFilename = f"{themeID}.json"
        count = 1
        while True:
            if not os.path.exists(os.path.join(self._env.dataDir, currentFilename)):
                return currentFilename
            currentFilename = f"{themeID}{count}.json"
            count += 1

    def doNameExists(self, name: str) -> bool:
        for i in self._themeDict.values():
            if name.lower() == i[0]["name"].lower():
                return True
        return False
