from jdTextEdit.api.StatusBarWidgetBase import StatusBarWidgetBase
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QLabel


class LanguageWidget(QLabel, StatusBarWidgetBase):
    @staticmethod
    def getID() -> str:
        return "builtin.language"

    @staticmethod
    def getName() -> str:
        return QCoreApplication.translate("StatusBarWidgets", "Language")

    def updateWidget(self, mainWindow):
        self.setText(mainWindow.getTextEditWidget().languageName)
