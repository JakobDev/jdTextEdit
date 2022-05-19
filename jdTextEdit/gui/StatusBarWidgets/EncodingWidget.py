from jdTextEdit.api.StatusBarWidgetBase import StatusBarWidgetBase
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QLabel


class EncodingWidget(QLabel, StatusBarWidgetBase):
    @staticmethod
    def getID() -> str:
        return "builtin.encoding"

    @staticmethod
    def getName() -> str:
        return QCoreApplication.translate("StatusBarWidgets", "Encoding")

    def updateWidget(self, mainWindow):
        self.setText(mainWindow.getTextEditWidget().usedEncoding)
