from PyQt6.QtWidgets import QWidget, QGroupBox, QDialog, QComboBox, QLabel, QLineEdit, QPushButton, QFormLayout, QHBoxLayout, QVBoxLayout
from jdTextEdit.Functions import uppercaseFirstLetter, getLexerStyles
from jdTextEdit.gui.Widgets.ListWidgetLayout import ListWidgetLayout
from jdTextEdit.gui.Widgets.ColorButton import ColorButton
from jdTextEdit.core.FileTheme import FileTheme
from jdTextEdit.gui.CodeEdit import CodeEdit
from typing import Optional, TYPE_CHECKING
from PyQt6.QtCore import QCoreApplication
from PyQt6.Qsci import QsciLexer
from PyQt6.QtGui import QColor
import json
import os


if TYPE_CHECKING:
    from jdTextEdit.gui.Windows.ManageThemesWindow.ManageThemeListWindow import ManageThemeListWindow
    from jdTextEdit.gui.Windows.ManageThemesWindow.FileThemeDictType import FileThemeDict
    from jdTextEdit.Environment import Environment


class GlobalColorsWidget(QGroupBox):
    def __init__(self, editThemeWindow: "EditThemeWindow"):
        super().__init__()

        self._colorList = [
            "textColor",
            "backgroundColor",
            "selectionForegroundColor",
            "selectionBackgroundColor",
            "marginsBackgroundColor",
            "marginsForegroundColor",
            "caretColor"
        ]

        self._widgetList = []
        mainLayout = QFormLayout()
        for i in self._colorList:
            button = ColorButton()
            button.clicked.connect(editThemeWindow.updatePreview)
            self._widgetList.append(button)
            mainLayout.addRow(uppercaseFirstLetter(i), button)

        self.setLayout(mainLayout)

    def getThemeData(self) -> dict[str, str]:
        themeData = {}
        for count, i in enumerate(self._colorList):
            color = self._widgetList[count].getColor()
            if color.isValid():
                themeData[i] = color.name()
        return themeData

    def loadThemeData(self, themeData: dict[str, str]):
        for count, i in enumerate(self._colorList):
            if i in themeData:
                self._widgetList[count].setColor(QColor(themeData[i]))


class SingleLexerWidget(QWidget):
    def __init__(self, lexer: QsciLexer, editThemeWindow: "EditThemeWindow"):
        super().__init__()

        self._mainLayout = QFormLayout()
        for i in getLexerStyles(lexer).keys():
            button = ColorButton()
            button.clicked.connect(editThemeWindow.updatePreview)
            self._mainLayout.addRow(i, button)

        self.setLayout(self._mainLayout)

    def getThemeData(self) -> dict[str, str]:
        themeData = {}
        for i in range(self._mainLayout.count()):
            try:
                name = self._mainLayout.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().text()
            except AttributeError:
                continue
            color = self._mainLayout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget().getColor()
            if color.isValid():
                themeData[name] = color.name()
        return themeData


class LexerThemeWidget(QGroupBox):
    def __init__(self, env: "Environment", editThemeWindow: "EditThemeWindow"):
        super().__init__()

        self._listWidget = ListWidgetLayout()

        self._jakobDict = {}
        for i in env.languageList:
            lexer = i.getLexer()
            w = SingleLexerWidget(lexer, editThemeWindow)
            self._jakobDict[lexer.language()] = w
            self._listWidget.addWidget(lexer.language(), w, scrollable=True)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self._listWidget)

        self.setLayout(mainLayout)

    def getThemeData(self) -> dict[str, dict[str, str]]:
        themeData = {}
        for key, value in self._jakobDict.items():
            data = value.getThemeData()
            if len(data) != 0:
                themeData[key] = data
        return themeData


class PreviewWidget(QGroupBox):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self._env = env

        self._languageBox = QComboBox()
        self._previewEdit = CodeEdit(env, preview=True)

        self._languageBox.addItem("Plain", "plain")
        for i in env.languageList:
            self._languageBox.addItem(i.getName(), i.getID())

        self._previewEdit.updateSettings(env.settings)

        self._languageBox.currentIndexChanged.connect(self._languageChanged)

        languageLayout = QHBoxLayout()
        languageLayout.addWidget(QLabel(QCoreApplication.translate("EditThemeWindow", "Language:")))
        languageLayout.addWidget(self._languageBox)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(languageLayout)
        mainLayout.addWidget(self._previewEdit)

        self.setLayout(mainLayout)

    def _languageChanged(self) -> None:
        if self._languageBox.currentData() == "plain":
            self._previewEdit.removeLanguage()
        else:
            self._previewEdit.setLanguage(self._env.getLanguageByID(self._languageBox.currentData()))

    def getCodeEdit(self) -> CodeEdit:
        return self._previewEdit


class EditThemeWindow(QDialog):
    def __init__(self, env: "Environment", themeListWidget: "ManageThemeListWindow", currentTheme: Optional["FileThemeDict"], filename: Optional[str]):
        super().__init__()
        self._env = env

        self._themeListWidget = themeListWidget
        self._currentFilename = filename

        self._nameEdit = QLineEdit()
        self._globalWidget = GlobalColorsWidget(self)
        self._lexerWidget = LexerThemeWidget(env, self)
        self._previewWidget = PreviewWidget(env)
        okButton = QPushButton(QCoreApplication.translate("EditThemeWindow", "OK"))
        cancelButton = QPushButton(QCoreApplication.translate("EditThemeWindow", "Cancel"))

        if currentTheme is not None:
            self._currentID = currentTheme["id"]
            self._nameEdit.setText(currentTheme["name"])
            self._globalWidget.loadThemeData(currentTheme["global"])
        else:
            self._currentID = None

        okButton.clicked.connect(self._okButtonClicked)
        cancelButton.clicked.connect(self.close)

        self.updatePreview()

        nameLayout = QHBoxLayout()
        nameLayout.addWidget(QLabel(QCoreApplication.translate("EditThemeWindow", "Name:")))
        nameLayout.addWidget(self._nameEdit)

        colorLayout = QHBoxLayout()
        colorLayout.addWidget(self._globalWidget)
        colorLayout.addWidget(self._lexerWidget)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        if env.settings.get("swapOkCancel"):
            buttonLayout.addWidget(okButton)
            buttonLayout.addWidget(cancelButton)
        else:
            buttonLayout.addWidget(cancelButton)
            buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(nameLayout)
        mainLayout.addLayout(colorLayout)
        mainLayout.addWidget(self._previewWidget)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def _getThemeData(self) -> "FileThemeDict":
        themeData: "FileThemeDict" = {
            "id": "",
            "name": self._nameEdit.text(),
            "global": self._globalWidget.getThemeData(),
            "lexer": self._lexerWidget.getThemeData()
        }
        return themeData

    def _okButtonClicked(self):
        if self._currentID is not None:
            themeID = self._currentID
        else:
            themeID = self._themeListWidget.generateThemeID(self._nameEdit.text())

        filename = self._currentFilename or self._themeListWidget.getFreeFilename(themeID)

        themeData = self._getThemeData()
        themeData["id"] = themeID

        self._themeListWidget.updateTheme(themeData, filename=filename)
        self._themeListWidget.updateListWidget()

        with open(os.path.join(self._env.dataDir, "themes", filename), "w", encoding="utf-8") as f:
            json.dump(themeData, f, ensure_ascii=False, indent=4)

        self.close()

    def updatePreview(self) -> None:
        themeData = self._getThemeData()
        previewTheme = FileTheme.fromDict(themeData)
        self._previewWidget.getCodeEdit().setCustomTheme(previewTheme)
