from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QSpinBox, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QLayout
from jdTextEdit.Functions import getThemeIcon
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment
    from jdTextEdit.gui.CodeEdit import CodeEdit


class SearchWindow(QWidget):
    def __init__(self, env: "Environment"):
        super().__init__()
        self.searchEdit = QLineEdit()
        self.regEx = QCheckBox(QCoreApplication.translate("SearchWindow", "Regular Expression"))
        self.caseSensitive = QCheckBox(QCoreApplication.translate("SearchWindow", "Match case"))
        self.wholeWord = QCheckBox(QCoreApplication.translate("SearchWindow", "Match entire word only"))
        self.wrap = QCheckBox(QCoreApplication.translate("SearchWindow", "Wrap around"))
        self.backward = QCheckBox(QCoreApplication.translate("SearchWindow", "Search backwards"))
        self.showHiddenText = QCheckBox(QCoreApplication.translate("SearchWindow", "Show text if hidden"))
        self.searchRange = QCheckBox(QCoreApplication.translate("SearchWindow", "Search from a certain range"))
        self.lineLabel = QLabel(QCoreApplication.translate("SearchWindow", "Search at Line:"))
        self.indexLabel = QLabel(QCoreApplication.translate("SearchWindow", "Search at Column:"))
        self.lineSpinBox = QSpinBox()
        self.indexSpinBox = QSpinBox()
        self.closeButton = QPushButton(QCoreApplication.translate("SearchWindow", "Close"))
        self.searchButton = QPushButton(QCoreApplication.translate("SearchWindow", "Find"))

        self.wrap.setChecked(True)
        self.showHiddenText.setChecked(True)

        self.lineSpinBox.setRange(0, 2147483647)
        self.indexSpinBox.setRange(0, 2147483647)

        self.lineSpinBox.setValue(0)
        self.indexSpinBox.setValue(0)

        self.closeButton.setIcon(getThemeIcon(env, "window-close"))
        self.searchButton.setIcon(getThemeIcon(env, "edit-find"))

        self.searchRange.stateChanged.connect(self.searchRangeEnableUpdated)
        self.closeButton.clicked.connect(self.close)
        self.searchButton.clicked.connect(self.searchButtonClicked)

        searchTextLayout = QHBoxLayout()
        searchTextLayout.addWidget(QLabel(QCoreApplication.translate("SearchWindow", "Search for:")))
        searchTextLayout.addWidget(self.searchEdit)

        numberLayout = QGridLayout()
        numberLayout.addWidget(self.lineLabel, 0, 0)
        numberLayout.addWidget(self.lineSpinBox, 0, 1)
        numberLayout.addWidget(self.indexLabel, 1, 0)
        numberLayout.addWidget(self.indexSpinBox, 1, 1)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.closeButton)
        buttonLayout.addWidget(self.searchButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(searchTextLayout)
        mainLayout.addWidget(self.regEx)
        mainLayout.addWidget(self.caseSensitive)
        mainLayout.addWidget(self.wholeWord)
        mainLayout.addWidget(self.wrap)
        mainLayout.addWidget(self.backward)
        mainLayout.addWidget(self.showHiddenText)
        mainLayout.addWidget(self.searchRange)
        mainLayout.addLayout(numberLayout)
        mainLayout.addLayout(buttonLayout)
        mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(mainLayout)
        self.setWindowTitle(QCoreApplication.translate("SearchWindow", "Find"))

    def searchButtonClicked(self) -> None:
        if self.searchRange.isChecked():
            line = self.lineSpinBox.value()
            index = self.indexSpinBox.value()
        else:
            line = -1
            index = -1

        self.editWidget.findFirst(
            self.searchEdit.text(),
            self.regEx.isChecked(),
            self.caseSensitive.isChecked(),
            self.wholeWord.isChecked(),
            self.wrap.isChecked(),
            not self.backward.isChecked(),
            line,
            index,
            self.showHiddenText.isChecked()
        )

    def searchRangeEnableUpdated(self):
        enabled = self.searchRange.isChecked()
        self.lineLabel.setEnabled(enabled)
        self.indexLabel.setEnabled(enabled)
        self.lineSpinBox.setEnabled(enabled)
        self.indexSpinBox.setEnabled(enabled)

    def openWindow(self, editWidget: "CodeEdit"):
        self.editWidget = editWidget
        self.searchRangeEnableUpdated()
        self.show()
        QApplication.setActiveWindow(self)
