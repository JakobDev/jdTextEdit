from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPlainTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QLayout

class SearchAndReplaceWindow(QWidget):
    def __init__(self,env):
        super().__init__()
        self.searchEdit = QPlainTextEdit()
        self.replaceEdit = QPlainTextEdit()
        self.cancelButton = QPushButton(env.translate("button.cancel"))
        self.okButton = QPushButton(env.translate("button.ok"))

        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        self.okButton.clicked.connect(self.okButtonClicked)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addStretch(1)
        if env.settings.get("swapOkCancel"):
            self.buttonLayout.addWidget(self.okButton)
            self.buttonLayout.addWidget(self.cancelButton)
        else:
            self.buttonLayout.addWidget(self.cancelButton)
            self.buttonLayout.addWidget(self.okButton)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(QLabel(env.translate("searchAndReplaceWindow.label.searchFor")))
        self.mainLayout.addWidget(self.searchEdit)
        self.mainLayout.addWidget(QLabel(env.translate("searchAndReplaceWindow.label.replaceWith")))
        self.mainLayout.addWidget(self.replaceEdit)
        self.mainLayout.addLayout(self.buttonLayout)
        self.mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setWindowTitle(env.translate("searchAndReplaceWindow.title"))
        self.setLayout(self.mainLayout)

    def cancelButtonClicked(self):
        self.close()

    def okButtonClicked(self):
        text = self.textEdit.text()
        text = text.replace(self.searchEdit.toPlainText(),self.replaceEdit.toPlainText())
        self.textEdit.setText(text)
        self.close()

    def display(self, edit):
        self.show()
        self.textEdit = edit
        QApplication.setActiveWindow(self)
