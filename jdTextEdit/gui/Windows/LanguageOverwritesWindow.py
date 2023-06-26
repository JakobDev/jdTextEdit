from PyQt6.QtWidgets import QDialog, QWidget, QCheckBox, QPushButton, QLabel, QTabWidget, QHBoxLayout, QVBoxLayout
from jdTextEdit.api.Types import LanguageOverwriteEntry, LanguageOverwriteEntryData
from jdTextEdit.gui.Widgets.ListWidgetLayout import ListWidgetLayout
from jdTextEdit.gui.Widgets.TextListWidget import TextListWidget
from PyQt6.QtCore import Qt, QCoreApplication
from typing import cast, TYPE_CHECKING
import json
import os


if TYPE_CHECKING:
    from jdTextEdit.api.LanguageBase import LanguageBase
    from jdTextEdit.Environment import Environment


class LanguageOverwritesListWidget(QWidget):
    def __init__(self, defaultList: list[str], labelText: str) -> None:
        super().__init__()

        self._checkBox = QCheckBox(QCoreApplication.translate("LanguageOverwritesWindow", "Enable overwrite"))
        resetButton = QPushButton(QCoreApplication.translate("LanguageOverwritesWindow", "Reset"))
        self._listWidget = TextListWidget()
        self._defaultList = defaultList
        infoLabel = QLabel(labelText)

        infoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        infoLabel.setWordWrap(True)

        self._checkBox.stateChanged.connect(lambda: self._listWidget.setEnabled(self._checkBox.isChecked()))
        resetButton.clicked.connect(self._resetData)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(infoLabel)
        mainLayout.addWidget(self._checkBox)
        mainLayout.addWidget(self._listWidget)
        mainLayout.addWidget(resetButton)

        self.setLayout(mainLayout)

        self._resetData()

    def _resetData(self) -> None:
        self._checkBox.setChecked(False)
        self._listWidget.setEnabled(False)
        self._listWidget.setTextList(self._defaultList)

    def loadData(self, data: LanguageOverwriteEntryData) -> None:
        self._checkBox.setChecked(data["enabled"])
        self._listWidget.setTextList(data["textList"])
        self._listWidget.setEnabled(data["enabled"])

    def getData(self) -> LanguageOverwriteEntryData:
        return {"enabled": self._checkBox.isChecked(), "textList": self._listWidget.getTextList()}


class LanguageOverwritesTabWidget(QTabWidget):
    def __init__(self, lang: "LanguageBase") -> None:
        super().__init__()
        self._language = lang

        self._extensionsWidget = LanguageOverwritesListWidget(self._language.getExtensions(), QCoreApplication.translate("LanguageOverwritesWindow", "Filenames with this Extension are detected as the current Language"))
        self._starttextWidget = LanguageOverwritesListWidget(self._language.getStarttext(), QCoreApplication.translate("LanguageOverwritesWindow", "Files that start with this Text are detected as the current Language"))
        self._mimetypesWidget = LanguageOverwritesListWidget(self._language.getMimeType(), QCoreApplication.translate("LanguageOverwritesWindow", "Files that have this MimeType are detected as the current Language"))

        self.addTab(self._extensionsWidget, QCoreApplication.translate("LanguageOverwritesWindow", "Extensions"))
        self.addTab(self._starttextWidget, QCoreApplication.translate("LanguageOverwritesWindow", "Starts with"))
        self.addTab(self._mimetypesWidget, QCoreApplication.translate("LanguageOverwritesWindow", "MimeType"))

    def loadData(self, data: LanguageOverwriteEntry) -> None:
        if "extensions" in data:
            self._extensionsWidget.loadData(data["extensions"])

        if "starttext" in data:
            self._starttextWidget.loadData(data["starttext"])

        if "mimetypes" in data:
            self._mimetypesWidget.loadData(data["mimetypes"])

    def getData(self) -> LanguageOverwriteEntry:
        return {
            "extensions": self._extensionsWidget.getData(),
            "starttext": self._starttextWidget.getData(),
            "mimetypes": self._mimetypesWidget.getData()
        }

    def getLanguageID(self) -> str:
        return self._language.getID()


class LanguageOverwritesWindow(QDialog):
    def __init__(self, env: "Environment") -> None:
        super().__init__()

        self._env = env

        self._widgetList = ListWidgetLayout()
        okButton = QPushButton(QCoreApplication.translate("LanguageOverwritesWindow", "OK"))
        cancelButton = QPushButton(QCoreApplication.translate("LanguageOverwritesWindow", "Cancel"))

        for i in env.languageList:
            tabWidget = LanguageOverwritesTabWidget(i)
            tabWidget.loadData(self._env.languageOverwrites.get(i.getID(), {}))
            self._widgetList.addWidget(i.getName(), tabWidget)

        okButton.clicked.connect(self._okButtonClicked)
        cancelButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        if env.settings.get("swapOkCancel"):
            buttonLayout.addWidget(okButton)
            buttonLayout.addWidget(cancelButton)
        else:
            buttonLayout.addWidget(cancelButton)
            buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self._widgetList)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

        self.setWindowTitle(QCoreApplication.translate("LanguageOverwritesWindow", "Manage languages"))

    def _okButtonClicked(self) -> None:
        data = {}

        for i in self._widgetList.getWidgetList():
            i = cast(LanguageOverwritesTabWidget, i)
            data[i.getLanguageID()] = i.getData()

        with open(os.path.join(self._env.dataDir, "languageOverwrites.json"), "w", encoding="utf-8") as f:
            json.dump({"version": 1, "overwrites": data}, f, ensure_ascii=False, indent=4)

        self._env.languageOverwrites = data
        self.close()
