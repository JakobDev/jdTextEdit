from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QCheckBox, QHBoxLayout, QVBoxLayout, QLayout
from jdTextEdit.Functions import executeCommand
import os

class ExecuteCommandWindow(QWidget):
    def __init__(self, env):
        super().__init__()
        self.commandEdit = QLineEdit()
        okButton = QPushButton(env.translate("button.ok"))
        cancelButton = QPushButton(env.translate("button.cancel"))
        self.terminalCheckBox = QCheckBox(env.translate("executeCommandWindow.runTerminal"))
 
        okButton.clicked.connect(self.okButtonClicked)
        cancelButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("%url% - " + env.translate("executeCommand.label.url")))
        mainLayout.addWidget(QLabel("%path% - " + env.translate("executeCommand.label.path")))
        mainLayout.addWidget(QLabel("%directory% - " + env.translate("executeCommand.label.directory")))
        mainLayout.addWidget(QLabel("%filename% - " + env.translate("executeCommand.label.filename")))
        mainLayout.addWidget(QLabel("%selection% - " + env.translate("executeCommand.label.selection")))
        mainLayout.addWidget(self.commandEdit)
        mainLayout.addWidget(self.terminalCheckBox)
        if os.getenv("SNAP"):
            mainLayout.addWidget(QLabel(env.translate("executeCommand.label.snap")))
        mainLayout.addLayout(buttonLayout)
        mainLayout.setSizeConstraint(QLayout.SetFixedSize)

        self.setLayout(mainLayout)
        self.setWindowTitle(env.translate("executeCommandWindow.title"))

    def openWindow(self, editWidget):
        self.editWidget = editWidget
        self.show()
        QApplication.setActiveWindow(self)

    def okButtonClicked(self):
        executeCommand(self.commandEdit.text(),self.editWidget,bool(self.terminalCheckBox.checkState()))
        self.close()