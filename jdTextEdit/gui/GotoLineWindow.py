from PyQt6.QtWidgets import QDialog, QSpinBox, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QLayout
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment
    from jdTextEdit.gui.CodeEdit import CodeEdit


class GotoLineWindow(QDialog):
    def __init__(self, env: "Environment"):
        super().__init__()

        self.lineBox = QSpinBox()
        self.lineBox.setMinimum(1)
        okButton = QPushButton(env.translate("button.ok"))
        cancelButton = QPushButton(env.translate("button.cancel"))

        okButton.clicked.connect(self.okButtonClicked)
        cancelButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        if env.settings.get("swapOkCancel"):
            buttonLayout.addWidget(okButton)
            buttonLayout.addWidget(cancelButton)
        else:
            buttonLayout.addWidget(cancelButton)
            buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel(env.translate("gotoLineWindow.text")))
        mainLayout.addWidget(self.lineBox)
        mainLayout.addLayout(buttonLayout)
        mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(mainLayout)
        self.setWindowTitle(env.translate("gotoLineWindow.title"))

    def openWindow(self, editWidget: "CodeEdit") -> None:
        self.editWidget = editWidget
        self.lineBox.setValue(self.editWidget.cursorPosLine + 1)
        self.lineBox.setMaximum(self.editWidget.lines())
        self.exec()

    def okButtonClicked(self) -> None:
        try:
            self.editWidget.setCursorPosition(self.lineBox.value() - 1, 0)
            self.editWidget.ensureCursorVisible()
        except Exception:
            pass
        self.close()
