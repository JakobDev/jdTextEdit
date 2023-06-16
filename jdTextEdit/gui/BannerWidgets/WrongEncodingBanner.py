from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.gui.EditContainer import EditContainer
    from jdTextEdit.Environment import Environment


class WrongEncodingBanner(QWidget):
    def __init__(self, env: "Environment", parent: "EditContainer") -> None:
        super().__init__()
        self.env = env
        self.parent = parent

        reloadButton = QPushButton(QCoreApplication.translate("BannerWidgets", "Change to {{encoding}}").replace("{{encoding}}", env.settings.defaultEncoding))
        reloadButton.clicked.connect(self.changeEncoding)

        ignoreButton = QPushButton(QCoreApplication.translate("BannerWidgets", "Ignore"))
        ignoreButton.clicked.connect(lambda: parent.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(QCoreApplication.translate("BannerWidgets", "The encoding does not correspond to the default settings")))
        mainLayout.addStretch(1)
        mainLayout.addWidget(reloadButton)
        mainLayout.addWidget(ignoreButton)

        self.setLayout(mainLayout)

    def changeEncoding(self) -> None:
        self.parent.getCodeEditWidget().setUsedEncoding(self.env.settings.defaultEncoding)
        self.parent.removeBanner(self)
