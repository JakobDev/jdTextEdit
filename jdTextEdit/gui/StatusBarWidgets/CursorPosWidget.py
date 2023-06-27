from jdTextEdit.api.StatusBarWidgetBase import StatusBarWidgetBase
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QLabel
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.gui.MainWindow import MainWindow


class CursorPosWidget(QLabel, StatusBarWidgetBase):
    @staticmethod
    def getID() -> str:
        return "builtin.cursorPos"

    @staticmethod
    def getName() -> str:
        return QCoreApplication.translate("StatusBarWidgets", "Cursor position")

    def updateWidget(self, mainWindow: "MainWindow") -> None:
        editWidget = mainWindow.getTextEditWidget()

        self.setText(QCoreApplication.translate("StatusBarWidgets", "Ln {line}, Col {column}").replace("{line}", str(editWidget.cursorPosLine + 1)).replace("{column}", str(editWidget.cursorPosIndex + 1)))
