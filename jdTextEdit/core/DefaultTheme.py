from jdTextEdit.Functions import getLexerStyles
from jdTextEdit.api.ThemeBase import ThemeBase
from typing import Optional, TYPE_CHECKING
from PyQt6.QtCore import QCoreApplication
from PyQt6.Qsci import QsciLexer
from PyQt6.QtGui import QColor


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment
    from jdTextEdit.gui.CodeEdit import CodeEdit


class DefaultTheme(ThemeBase):
    def __init__(self, env: "Environment") -> None:
        self.env = env

    def applyTheme(self, editWidget: "CodeEdit", lexer: Optional[QsciLexer]) -> None:
        editWidget.setColor(QColor("#000000"))
        editWidget.setPaper(QColor("#FFFFFF"))
        editWidget.setSelectionForegroundColor(QColor("#FFFFFF"))
        editWidget.setSelectionBackgroundColor(QColor("#308CC6"))
        editWidget.setMarginsBackgroundColor(QColor("#cccccc"))
        editWidget.setMarginsForegroundColor(QColor("#000000"))
        editWidget.setCaretLineBackgroundColor(QColor("#ffff00"))

        if not lexer:
            return

        lexer.setPaper(QColor("#FFFFFF"))
        lexer.setColor(QColor("#000000"))
        lexer.setDefaultPaper(QColor("#FFFFFF"))
        lexer.setDefaultColor(QColor("#000000"))
        base = editWidget.getLanguage().getLexer()
        for i in getLexerStyles(base).values():
            baseColor = base.color(i)
            lexer.setColor(baseColor, i)

    def getName(self) -> str:
        return QCoreApplication.translate("DefaultTheme", "Default")

    def getID(self) -> str:
        return "builtin.default"
