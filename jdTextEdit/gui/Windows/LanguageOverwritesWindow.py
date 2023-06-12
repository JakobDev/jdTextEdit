from PyQt6.QtWidgets import QDialog, QWidget, QCheckBox, QPushButton, QTabWidget, QHBoxLayout, QVBoxLayout
from jdTextEdit.gui.Widgets.ListWidgetLayout import ListWidgetLayout
from jdTextEdit.gui.Widgets.TextListWidget import TextListWidget
from PyQt6.QtCore import QCoreApplication
from typing import cast, TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.api.LanguageBase import LanguageBase
    from jdTextEdit.Environment import Environment


class LanguageOverwritesListWidget(QWidget):
    def __init__(self):
        super().__init__()

        self._checkBox = QCheckBox()
        self._listWidget = TextListWidget()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self._checkBox)
        mainLayout.addWidget(self._listWidget)

        self.setLayout(mainLayout)

    def loadData(self, enabled: bool, textList: list[str]):
        self._checkBox.setChecked(enabled)
        self._listWidget.setTextList(textList)

    def getData(self) -> tuple[bool, list[str]]:
        return self._checkBox.isChecked(), self._listWidget.getTextList()


class LanguageOverwritesTabWidget(QTabWidget):
    def __init__(self, lang: "LanguageBase"):
        super().__init__()
        self._language = lang

        self._extensionsWidget = LanguageOverwritesListWidget()

        self.addTab(self._extensionsWidget, "FFF")

    def loadData(self, data) -> None:
        if len(data.get("extensions", [])) != 0:
            pass
        else:
            self._extensionsWidget.loadData(True, self._language.getExtensions())

    def getData(self):
        return "HHH"

    def getLanguageID(self) -> str:
        return self._language.getID()


class LanguageOverwritesWindow(QDialog):
    def __init__(self, env: "Environment"):
        super().__init__()

        self._widgetList = ListWidgetLayout()
        okButton = QPushButton(QCoreApplication.translate("LanguageOverwritesWindow", "OK"))
        cancelButton = QPushButton(QCoreApplication.translate("LanguageOverwritesWindow", "Cancel"))

        for i in env.languageList:
            tabWidget = LanguageOverwritesTabWidget(i)
            tabWidget.loadData({})
            self._widgetList.addWidget(i.getName(), tabWidget)

        okButton.clicked.connect(self._okButtonClicked)

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

    def _okButtonClicked(self) -> None:
        data = {}
        for i in cast(LanguageOverwritesTabWidget, self._widgetList.getWidgetList()):
            data[i.getLanguageID()] = i.getData()
        print(data)
