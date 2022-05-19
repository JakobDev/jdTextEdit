from jdTextEdit.api.StatusBarWidgetBase import StatusBarWidgetBase
from PyQt6.QtCore import QCoreApplication
from PyQt6.Qsci import QsciScintilla
from PyQt6.QtWidgets import QLabel


class EolWidget(QLabel, StatusBarWidgetBase):
    @staticmethod
    def getID() -> str:
        return "builtin.eol"

    @staticmethod
    def getName() -> str:
        return QCoreApplication.translate("StatusBarWidgets", "End of Line")

    def updateWidget(self, mainWindow):
        eolMode = mainWindow.getTextEditWidget().eolMode()
        if eolMode == QsciScintilla.EolMode.EolWindows:
            self.setText("CRLF")
        elif eolMode == QsciScintilla.EolMode.EolUnix:
            self.setText("LF")
        elif eolMode == QsciScintilla.EolMode.EolMac:
            self.setText("CR")
