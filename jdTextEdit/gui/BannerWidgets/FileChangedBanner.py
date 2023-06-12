from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout
from typing import  TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.gui.EditContainer import EditContainer
    from jdTextEdit.Environment import Environment


class FileChangedBanner(QWidget):
    def __init__(self,env: "Environment", parent: "EditContainer"):
        super().__init__()
        self.env = env
        self.parent = parent

        reloadButton = QPushButton(env.translate("fileChangedBanner.button.reload"))
        reloadButton.clicked.connect(self._reloadFile)

        ignoreButton = QPushButton(env.translate("button.ignore"))
        ignoreButton.clicked.connect(lambda: parent.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(env.translate("fileChangedBanner.text")))
        mainLayout.addStretch(1)
        mainLayout.addWidget(reloadButton)
        mainLayout.addWidget(ignoreButton)

        self.setLayout(mainLayout)

    def _reloadFile(self):
        self.env.mainWindow.openFile(self.parent.getCodeEditWidget().getFilePath(), reload=True)
        self.parent.removeBanner(self)
