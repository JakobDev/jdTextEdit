from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout

class EditorconfigBanner(QWidget):
    def __init__(self,env,container):
        super().__init__()

        okButton = QPushButton(env.translate("button.ok"))

        okButton.clicked.connect(lambda: container.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(env.translate("editorconfigBanner.text")))
        mainLayout.addStretch(1)
        mainLayout.addWidget(okButton)

        self.setLayout(mainLayout)
