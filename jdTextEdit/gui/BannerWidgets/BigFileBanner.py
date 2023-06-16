from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.gui.EditContainer import EditContainer


class BigFileBanner(QWidget):
    def __init__(self, parent: "EditContainer") -> None:
        super().__init__()

        self.parent = parent

        okButton = QPushButton(QCoreApplication.translate("BannerWidgets", "OK"))

        okButton.clicked.connect(lambda: parent.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(QCoreApplication.translate("BannerWidgets", "Due to the size of the file some features have been disabled")))
        mainLayout.addStretch(1)
        mainLayout.addWidget(okButton)

        self.setLayout(mainLayout)
