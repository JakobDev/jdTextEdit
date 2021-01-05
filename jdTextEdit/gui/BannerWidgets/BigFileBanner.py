from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout

class BigFileBanner(QWidget):
    def __init__(self,env,parent):
        super().__init__()
        self.env = env
        self.parent = parent

        okButton = QPushButton("OK")

        okButton.clicked.connect(lambda: parent.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(env.translate("bigFileBanner.text")))
        mainLayout.addStretch(1)
        mainLayout.addWidget(okButton)

        self.setLayout(mainLayout)
