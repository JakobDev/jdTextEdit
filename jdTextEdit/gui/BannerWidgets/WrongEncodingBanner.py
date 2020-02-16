from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout

class WrongEncodingBanner(QWidget):
    def __init__(self,env,parent):
        super().__init__()
        self.env = env
        self.parent = parent

        reloadButton = QPushButton(env.translate("button.changeTo") % self.env.settings.defaultEncoding)
        reloadButton.clicked.connect(self.changeEncoding)

        ignoreButton = QPushButton(env.translate("button.ignore"))
        ignoreButton.clicked.connect(lambda: parent.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(env.translate("wrongEncodingBanner.text")))
        mainLayout.addStretch(1)
        mainLayout.addWidget(reloadButton)
        mainLayout.addWidget(ignoreButton)

        self.setLayout(mainLayout)

    def changeEncoding(self):
        self.parent.getCodeEditWidget().setUsedEncoding(self.env.settings.defaultEncoding)
        self.parent.removeBanner(self)
