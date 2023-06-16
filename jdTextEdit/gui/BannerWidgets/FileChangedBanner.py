from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.gui.EditContainer import EditContainer
    from jdTextEdit.Environment import Environment


class FileChangedBanner(QWidget):
    def __init__(self,env: "Environment", parent: "EditContainer") -> None:
        super().__init__()
        self.env = env
        self.parent = parent

        reloadButton = QPushButton(QCoreApplication.translate("BannerWidgets", "Reload"))
        reloadButton.clicked.connect(self._reloadFile)

        ignoreButton = QPushButton(QCoreApplication.translate("BannerWidgets", "Ignore"))
        ignoreButton.clicked.connect(lambda: parent.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(QCoreApplication.translate("BannerWidgets", "This file was changed by another program")))
        mainLayout.addStretch(1)
        mainLayout.addWidget(reloadButton)
        mainLayout.addWidget(ignoreButton)

        self.setLayout(mainLayout)

    def _reloadFile(self) -> None:
        self.env.mainWindow.openFile(self.parent.getCodeEditWidget().getFilePath(), reload=True)
        self.parent.removeBanner(self)
