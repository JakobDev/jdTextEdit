from PyQt5.QtWidgets import QPlainTextEdit

class NotesWidget(QPlainTextEdit):
    def __init__(self,env):
        super().__init__()
        self.setPlaceholderText(env.translate("sidebar.notes.placeholderText"))
