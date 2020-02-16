from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout

class FileChangedBanner(QWidget):
    def __init__(self,env,parent):
        super().__init__()
        self.env = env
        self.parent = parent

        reloadButton = QPushButton(env.translate("fileChangedBanner.button.reload"))
        reloadButton.clicked.connect(self.reloadFile)

        ignoreButton = QPushButton(env.translate("button.ignore"))
        ignoreButton.clicked.connect(lambda: parent.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(env.translate("fileChangedBanner.text")))
        mainLayout.addStretch(1)
        mainLayout.addWidget(reloadButton)
        mainLayout.addWidget(ignoreButton)

        self.setLayout(mainLayout)

    def reloadFile(self):
        self.env.mainWindow.openFile(self.parent.getCodeEditWidget().getFilePath(),reload=True)
        self.parent.removeBanner(self)
