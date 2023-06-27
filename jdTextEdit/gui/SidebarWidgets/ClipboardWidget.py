from jdTextEdit.api.SidebarWidgetBase import SidebarWidgetBase
from PyQt6.QtWidgets import QApplication, QPlainTextEdit
from PyQt6.QtCore import QCoreApplication


class ClipboardWidget(QPlainTextEdit,SidebarWidgetBase):
    def __init__(self):
        super().__init__()

        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setPlaceholderText(QCoreApplication.translate("ClipboardWidget", "At the moment, there is nothing in the clipboard"))
        QApplication.clipboard().dataChanged.connect(self.clipboardChanged)
        self.clipboardChanged()

    def clipboardChanged(self):
        text = QApplication.clipboard().text()
        self.setPlainText(text)

    def getName(self) -> str:
        return QCoreApplication.translate("ClipboardWidget", "Clipboard")

    def getID(self) -> str:
        return "clipboard"