from jdTextEdit.api.SidebarWidgetBase import SidebarWidgetBase
from PyQt6.QtWidgets import QPlainTextEdit

class NotesWidget(QPlainTextEdit,SidebarWidgetBase):
    def __init__(self,env):
        super().__init__()
        self.env = env
        self.setPlaceholderText(env.translate("sidebar.notes.placeholderText"))

    def getName(self) -> str:
        return self.env.translate("sidebar.notes")

    def getID(self) -> str:
        return "notes"