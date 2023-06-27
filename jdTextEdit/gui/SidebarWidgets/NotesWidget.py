from jdTextEdit.api.SidebarWidgetBase import SidebarWidgetBase
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtCore import QCoreApplication


class NotesWidget(QPlainTextEdit, SidebarWidgetBase):
    def __init__(self) -> None:
        super().__init__()

        self.setPlaceholderText(QCoreApplication.translate("NotesWidget", "You can write down notes here"))

    def getName(self) -> str:
        return QCoreApplication.translate("NotesWidget", "Notes")

    def getID(self) -> str:
        return "notes"