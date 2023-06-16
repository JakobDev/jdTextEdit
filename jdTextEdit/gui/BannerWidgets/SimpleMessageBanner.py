from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.gui.EditContainer import EditContainer


class SimpleMessageBanner(QWidget):
    def __init__(self, parent: "EditContainer", text: str) -> None:
        super().__init__()

        okButton = QPushButton(QCoreApplication.translate("BannerWidgets", "OK"))

        okButton.clicked.connect(lambda: parent.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(text))
        mainLayout.addStretch(1)
        mainLayout.addWidget(okButton)

        self.setLayout(mainLayout)
