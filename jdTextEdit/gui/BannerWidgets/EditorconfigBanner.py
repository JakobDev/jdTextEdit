from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.gui.EditContainer import EditContainer


class EditorconfigBanner(QWidget):
    def __init__(self, container: "EditContainer") -> None:
        super().__init__()

        okButton = QPushButton(QCoreApplication.translate("BannerWidgets", "OK"))

        okButton.clicked.connect(lambda: container.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(QCoreApplication.translate("BannerWidgets", "Some settings from an .editorconfig file are used")))
        mainLayout.addStretch(1)
        mainLayout.addWidget(okButton)

        self.setLayout(mainLayout)
