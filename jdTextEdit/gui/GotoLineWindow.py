from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QLayout
from PyQt5.QtGui import QIntValidator

class GotoLineWindow(QWidget):
    def __init__(self, env):
        super().__init__()
        self.lineEdit = QLineEdit()
        okButton = QPushButton(env.translate("button.ok"))
        cancelButton = QPushButton(env.translate("button.cancel"))
        
        self.lineEdit.setValidator(QIntValidator())
        okButton.clicked.connect(self.okButtonClicked)
        cancelButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel(env.translate("gotoLineWindow.text")))
        mainLayout.addWidget(self.lineEdit)
        mainLayout.addLayout(buttonLayout)
        mainLayout.setSizeConstraint(QLayout.SetFixedSize)
        
        self.setLayout(mainLayout)
        self.setWindowTitle(env.translate("gotoLineWindow.title"))

    def openWindow(self, editWidget):
        self.editWidget = editWidget
        self.lineEdit.setText("")
        self.show()
        QApplication.setActiveWindow(self)

    def okButtonClicked(self):
        try:
            self.editWidget.setCursorPosition(int(self.lineEdit.text()) - 1,0)
            self.editWidget.ensureCursorVisible()
        except:
            pass
        self.close()
