from jdTextEdit.api.StatusBarWidgetBase import StatusBarWidgetBase
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QLabel


class PathWidget(QLabel, StatusBarWidgetBase):
    @staticmethod
    def getID() -> str:
        return "builtin.path"

    @staticmethod
    def getName() -> str:
        return QCoreApplication.translate("StatusBarWidgets", "Path")

    def updateWidget(self, mainWindow):
        self.setText(mainWindow.getTextEditWidget().filePath)
