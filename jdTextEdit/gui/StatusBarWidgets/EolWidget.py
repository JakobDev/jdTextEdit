from jdTextEdit.api.StatusBarWidgetBase import StatusBarWidgetBase
from PyQt6.QtCore import QCoreApplication
from PyQt6.Qsci import QsciScintilla
from PyQt6.QtGui import QMouseEvent, QCursor
from PyQt6.QtWidgets import QLabel
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.gui.MainWindow import MainWindow


class EolWidget(QLabel, StatusBarWidgetBase):
    def __init__(self):
        super().__init__()
        self._mainWindow = None

    @staticmethod
    def getID() -> str:
        return "builtin.eol"

    @staticmethod
    def getName() -> str:
        return QCoreApplication.translate("StatusBarWidgets", "End of Line")

    def updateWidget(self, mainWindow: "MainWindow") -> None:
        self._mainWindow = mainWindow
        eolMode = mainWindow.getTextEditWidget().eolMode()
        if eolMode == QsciScintilla.EolMode.EolWindows:
            self.setText("CRLF")
        elif eolMode == QsciScintilla.EolMode.EolUnix:
            self.setText("LF")
        elif eolMode == QsciScintilla.EolMode.EolMac:
            self.setText("CR")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._mainWindow.eolModeMenu.popup(QCursor.pos())

