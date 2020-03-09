from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout
from PyQt5.Qsci import QsciScintilla

class WrongEolBanner(QWidget):
    def __init__(self,env,parent):
        super().__init__()
        self.env = env
        self.parent = parent
        self.editWidget = parent.getCodeEditWidget()

        eolNames = ["Windows","Unix","Mac"]
        reloadButton = QPushButton(env.translate("button.changeTo") % eolNames[self.editWidget.settings.defaultEolMode])
        reloadButton.clicked.connect(self.changeEol)

        ignoreButton = QPushButton(env.translate("button.ignore"))
        ignoreButton.clicked.connect(lambda: parent.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(env.translate("wrongEolBanner.text")))
        mainLayout.addStretch(1)
        mainLayout.addWidget(reloadButton)
        mainLayout.addWidget(ignoreButton)

        self.setLayout(mainLayout)

    def changeEol(self):
        eolModeList = [QsciScintilla.EolWindows,QsciScintilla.EolUnix,QsciScintilla.EolMac]
        self.editWidget.changeEolMode(eolModeList[self.editWidget.settings.defaultEolMode])
        self.parent.removeBanner(self)
