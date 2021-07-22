from jdTextEdit.api.SidebarWidgetBase import SidebarWidgetBase
from PyQt6.QtWidgets import QApplication, QPlainTextEdit

class ClipboardWidget(QPlainTextEdit,SidebarWidgetBase):
    def __init__(self, env):
        super().__init__()
        self.env = env
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setPlaceholderText(env.translate("sidebar.clipboard.placeholderText"))
        QApplication.clipboard().dataChanged.connect(self.clipboardChanged)
        self.clipboardChanged()

    def clipboardChanged(self):
        text = QApplication.clipboard().text()
        self.setPlainText(text)

    def getName(self) -> str:
        return self.env.translate("sidebar.clipboard")

    def getID(self) -> str:
        return "clipboard"