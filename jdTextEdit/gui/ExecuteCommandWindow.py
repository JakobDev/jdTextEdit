from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QCheckBox, QHBoxLayout, QVBoxLayout, QLayout
from jdTextEdit.Functions import executeCommand
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment
    from jdTextEdit.gui.CodeEdit import CodeEdit


class ExecuteCommandWindow(QWidget):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env

        self.commandEdit = QLineEdit()
        okButton = QPushButton(QCoreApplication.translate("ExecuteCommandWindow", "OK"))
        cancelButton = QPushButton(QCoreApplication.translate("ExecuteCommandWindow", "Cancel"))
        self.terminalCheckBox = QCheckBox(QCoreApplication.translate("ExecuteCommandWindow", "Execute in Terminal"))

        okButton.clicked.connect(self.okButtonClicked)
        cancelButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("%url% - " + QCoreApplication.translate("ExecuteCommandWindow", "Full URL of the currently active file")))
        mainLayout.addWidget(QLabel("%path% - " + QCoreApplication.translate("ExecuteCommandWindow", "Full path of the currently active file")))
        mainLayout.addWidget(QLabel("%directory% - " + QCoreApplication.translate("ExecuteCommandWindow", "Directory of the currently active file")))
        mainLayout.addWidget(QLabel("%filename% - " + QCoreApplication.translate("ExecuteCommandWindow", "Name of the currently active file")))
        mainLayout.addWidget(QLabel("%selection% - " + QCoreApplication.translate("ExecuteCommandWindow", "Currently selected text")))
        mainLayout.addWidget(self.commandEdit)
        mainLayout.addWidget(self.terminalCheckBox)
        mainLayout.addLayout(buttonLayout)
        mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(mainLayout)
        self.setWindowTitle(QCoreApplication.translate("ExecuteCommandWindow", "Execute Command"))

    def openWindow(self, editWidget: "CodeEdit") -> None:
        self.editWidget = editWidget
        self.show()
        QApplication.setActiveWindow(self)

    def okButtonClicked(self) -> None:
        executeCommand(self.env, self.commandEdit.text(), self.editWidget, self.terminalCheckBox.isChecked())
        self.close()
