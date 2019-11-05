from PyQt5.QtWidgets import QApplication, QPlainTextEdit

class ClipboardWidget(QPlainTextEdit):
    def __init__(self, env):
        super().__init__()
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setPlaceholderText(env.translate("sidebar.clipboard.placeholderText"))
        QApplication.clipboard().dataChanged.connect(self.clipboardChanged)
        self.clipboardChanged()
    
    def clipboardChanged(self):
        text = QApplication.clipboard().text()
        self.setPlainText(text)
