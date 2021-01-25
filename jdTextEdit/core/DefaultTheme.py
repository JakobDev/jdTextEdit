from jdTextEdit.api.ThemeBase import ThemeBase
from PyQt5.QtGui import QColor

class DefaultTheme(ThemeBase):
    def __init__(self,env):
        self.env = env

    def applyTheme(self,editWidget,lexer):
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
        lexer.setDefaultPaper(QColor("#FFFFFF"))
        lexer.setDefaultColor(QColor("#000000"))
        base = editWidget.getLanguage().getLexer()
        for attr in base.__dir__():
            if isinstance(getattr(base,attr),int):
                colorID = getattr(base,attr)
                baseColor = base.color(colorID)
                lexer.setColor(baseColor,colorID)

    def getName(self):
        return self.env.translate("settingsWindow.style.theme.default")

    def getID(self):
        return "builtin.default"
