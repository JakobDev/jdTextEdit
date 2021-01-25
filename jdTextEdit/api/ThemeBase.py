from jdTextEdit.gui.CodeEdit import CodeEdit
from PyQt5.Qsci import QsciLexer

class ThemeBase():
    def applyTheme(self,editWidget: CodeEdit, lexer: QsciLexer):
        pass

    def getName(self) -> str:
        return "Unknown"

    def getID(self) -> str:
        return "unknown"
