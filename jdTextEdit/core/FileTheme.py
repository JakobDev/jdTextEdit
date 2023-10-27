from jdTextEdit.Functions import readJsonFile, getLexerStyles
from jdTextEdit.core.Logger import getGlobalLogger
from jdTextEdit.api.ThemeBase import ThemeBase
from PyQt6.QtGui import QColor
import sys
import os


class FileTheme(ThemeBase):
    def __init__(self, path: str):
        if path is None:
            return
        self.themeData = readJsonFile(path, None)
        if not self.themeData:
            raise BaseException
        if "id" not in self.themeData:
            getGlobalLogger().error(f"{os.path.basename(path)} must contain key id")
            raise BaseException
        if "name" not in self.themeData:
            getGlobalLogger().error(f"{os.path.basename(path)} must contain key name")
            raise BaseException

    @classmethod
    def fromDict(cls, data):
        theme = cls(None)
        theme.themeData = data
        return theme

    def applyTheme(self, editWidget, lexer) -> None:
        if "global" in self.themeData:
            editWidget.setColor(QColor(self.themeData["global"].get("textColor", "#000000")))
            editWidget.setPaper(QColor(self.themeData["global"].get("backgroundColor", "#FFFFFF")))
            editWidget.setSelectionForegroundColor(QColor(self.themeData["global"].get("selectionForegroundColor", "#FFFFFF")))
            editWidget.setSelectionBackgroundColor(QColor(self.themeData["global"].get("selectionBackgroundColor", "#308CC6")))
            editWidget.setMarginsBackgroundColor(QColor(self.themeData["global"].get("marginsBackgroundColor", "#cccccc")))
            editWidget.setMarginsForegroundColor(QColor(self.themeData["global"].get("marginsForegroundColor", "#000000")))
            editWidget.setCaretLineBackgroundColor(QColor(self.themeData["global"].get("caretColor", "#ffff00")))
        if not lexer:
            return
        if "global" in self.themeData:
            lexer.setPaper(QColor(self.themeData["global"].get("backgroundColor", "#FFFFFF")))
            lexer.setColor(QColor(self.themeData["global"].get("textColor", "#000000")))
            lexer.setDefaultPaper(QColor(self.themeData["global"].get("backgroundColor", "#FFFFFF")))
            lexer.setDefaultColor(QColor(self.themeData["global"].get("textColor", "#000000")))
        lexerLanguage = lexer.language()
        if lexerLanguage not in self.themeData["lexer"]:
            return
        for key, value in getLexerStyles(lexer).items():
            if key in self.themeData["lexer"][lexerLanguage]:
                lexer.setColor(QColor(self.themeData["lexer"][lexerLanguage][key]), value)

    def getName(self) -> str:
        return self.themeData["name"]

    def getID(self) -> str:
        return self.themeData["id"]
