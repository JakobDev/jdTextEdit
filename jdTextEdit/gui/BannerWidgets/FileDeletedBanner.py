from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.gui.EditContainer import EditContainer


class FileDeletedBanner(QWidget):
    def __init__(self, parent: "EditContainer") -> None:
        super().__init__()
        self.parent = parent

        closeButton = QPushButton(QCoreApplication.translate("BannerWidgets", "Close File"))
        closeButton.clicked.connect(lambda: parent.setParent(None))

        ignoreButton = QPushButton(QCoreApplication.translate("BannerWidgets", "Ignore"))
        ignoreButton.clicked.connect(lambda: parent.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(QCoreApplication.translate("BannerWidgets", "This file was deleted by another program")))
        mainLayout.addStretch(1)
        mainLayout.addWidget(closeButton)
        mainLayout.addWidget(ignoreButton)

        self.setLayout(mainLayout)
