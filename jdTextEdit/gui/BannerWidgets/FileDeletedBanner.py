from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout

class FileDeletedBanner(QWidget):
    def __init__(self,env,parent):
        super().__init__()
        self.env = env
        self.parent = parent

        closeButton = QPushButton(env.translate("fileDeletedBanner.button.closeFile"))
        closeButton.clicked.connect(lambda: parent.setParent(None))

        ignoreButton = QPushButton(env.translate("button.ignore"))
        ignoreButton.clicked.connect(lambda: parent.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(env.translate("fileDeletedBanner.text")))
        mainLayout.addStretch(1)
        mainLayout.addWidget(closeButton)
        mainLayout.addWidget(ignoreButton)

        self.setLayout(mainLayout)