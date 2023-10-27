from jdTextEdit.api.StatusBarWidgetBase import StatusBarWidgetBase
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QLabel
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.gui.MainWindow import MainWindow


class LengthWidget(QLabel, StatusBarWidgetBase):
    @staticmethod
    def getID() -> str:
        return "builtin.length"

    @staticmethod
    def getName() -> str:
        return QCoreApplication.translate("StatusBarWidgets", "Document length")

    def updateWidget(self, mainWindow: "MainWindow") -> None:
        editWidget = mainWindow.getTextEditWidget()

        lines = editWidget.lines()
        if lines == 0:
            lines = 1

        self.setText(QCoreApplication.translate("StatusBarWidgets", "Length: {{length}} Lines: {{lines}}").replace("{{length}}", str(editWidget.length())).replace("{{lines}}", str(lines)))