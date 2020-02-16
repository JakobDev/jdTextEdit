from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QLayout

class SearchAndReplaceWindow(QWidget):
    def __init__(self,env):
        super().__init__()
        self.searchEdit = QLineEdit()
        self.replaceEdit = QLineEdit()
        self.cancelButton = QPushButton(env.translate("button.cancel"))
        self.okButton = QPushButton(env.translate("button.ok"))
        
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        self.okButton.clicked.connect(self.okButtonClicked)

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(env.translate("searchAndReplaceWindow.label.searchFor")),0,0)
        gridLayout.addWidget(self.searchEdit,0,1)
        gridLayout.addWidget(QLabel(env.translate("searchAndReplaceWindow.label.replaceWith")),1,0)
        gridLayout.addWidget(self.replaceEdit,1,1)
        
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.addWidget(self.okButton)
        
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(gridLayout)
        self.mainLayout.addLayout(self.buttonLayout)
        self.mainLayout.setSizeConstraint(QLayout.SetFixedSize)
        
        self.setWindowTitle(env.translate("searchAndReplaceWindow.title"))
        self.setLayout(self.mainLayout)
    
    def cancelButtonClicked(self):
        self.close()

    def okButtonClicked(self):
        text = self.textEdit.text()
        text = text.replace(self.searchEdit.text(),self.replaceEdit.text())
        self.textEdit.setText(text)
        self.close()

    def display(self, edit):
        self.show()
        self.textEdit = edit
        QApplication.setActiveWindow(self)