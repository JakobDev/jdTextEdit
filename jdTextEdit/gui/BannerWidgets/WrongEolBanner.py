from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import QCoreApplication
from PyQt6.Qsci import QsciScintilla
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.gui.EditContainer import EditContainer


class WrongEolBanner(QWidget):
    def __init__(self, parent: "EditContainer") -> None:
        super().__init__()
        self.parent = parent
        self.editWidget = parent.getCodeEditWidget()

        eolNames = ("Windows", "Unix", "Mac")
        reloadButton = QPushButton(QCoreApplication.translate("BannerWidgets", "Change to {{eol}}").replace("{{eol}}", eolNames[self.editWidget.settings.defaultEolMode]))
        reloadButton.clicked.connect(self.changeEol)

        ignoreButton = QPushButton(QCoreApplication.translate("BannerWidgets", "Ignore"))
        ignoreButton.clicked.connect(lambda: parent.removeBanner(self))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(QLabel(QCoreApplication.translate("BannerWidgets", "The end of line does not correspond to the default settings")))
        mainLayout.addStretch(1)
        mainLayout.addWidget(reloadButton)
        mainLayout.addWidget(ignoreButton)

        self.setLayout(mainLayout)

    def changeEol(self) -> None:
        eolModeList = (QsciScintilla.EolMode.EolWindows, QsciScintilla.EolMode.EolUnix, QsciScintilla.EolMode.EolMac)
        self.editWidget.changeEolMode(eolModeList[self.editWidget.settings.defaultEolMode])
        self.parent.removeBanner(self)
