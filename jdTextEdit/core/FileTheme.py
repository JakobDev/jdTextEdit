from jdTextEdit.api.ThemeBase import ThemeBase
from jdTextEdit.Functions import readJsonFile
from PyQt6.QtGui import QColor
import traceback
import sys
import os


class FileTheme(ThemeBase):
    def __init__(self,path):
        self.themeData = readJsonFile(path,None)
        if not self.themeData:
            raise BaseException
        if "id" not in self.themeData:
            print(f"{os.path.basename(path)} must contain key id", file=sys.stderr)
            raise BaseException
        if "name" not in self.themeData:
            print(f"{os.path.basename(path)} must contain key name", file=sys.stderr)
            raise BaseException

    def applyTheme(self,editWidget,lexer):
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
        for key,value in self.themeData["lexer"][lexerLanguage].items():
            try:
                colorID = getattr(lexer, key)
                lexer.setColor(QColor(value), colorID)
            except Exception as e:
                print(traceback.format_exc(), end="", file=sys.stderr)

    def getName(self):
        return self.themeData["name"]

    def getID(self):
        return self.themeData["id"]
