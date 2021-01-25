from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QSpinBox, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QLayout
from jdTextEdit.Functions import getThemeIcon, restoreWindowState
import math

class SearchWindow(QWidget):
    def __init__(self, env):
        super().__init__()
        self.searchEdit = QLineEdit()
        self.regEx = QCheckBox(env.translate("searchWindow.checkBox.regularExpression"))
        self.caseSensitive = QCheckBox(env.translate("searchWindow.checkBox.caseSensitive"))
        self.wholeWord = QCheckBox(env.translate("searchWindow.checkBox.wholeWord"))
        self.wrap = QCheckBox(env.translate("searchWindow.checkBox.wrap"))
        self.backward = QCheckBox(env.translate("searchWindow.checkBox.backwards"))
        self.showText = QCheckBox(env.translate("searchWindow.checkBox.showText"))
        self.searchRange = QCheckBox(env.translate("searchWindow.checkBox.searchRange"))
        self.lineLabel = QLabel(env.translate("searchWindow.label.searchLine"))
        self.indexLabel = QLabel(env.translate("searchWindow.label.searchColumn"))
        self.lineSpinBox = QSpinBox()
        self.indexSpinBox = QSpinBox()
        self.closeButton = QPushButton(env.translate("button.close"))
        self.searchButton = QPushButton(env.translate("searchWindow.button.search"))

        self.wrap.setChecked(True)
        self.showText.setChecked(True)

        self.lineSpinBox.setRange(0,2147483647)
        self.indexSpinBox.setRange(0,2147483647)

        self.lineSpinBox.setValue(0)
        self.indexSpinBox.setValue(0)

        self.closeButton.setIcon(getThemeIcon(env,"window-close"))
        self.searchButton.setIcon(getThemeIcon(env,"edit-find"))

        self.searchRange.stateChanged.connect(self.searchRangeEnableUpdated)
        self.closeButton.clicked.connect(self.close)
        self.searchButton.clicked.connect(self.searchButtonClicked)

        searchTextLayout = QHBoxLayout()
        searchTextLayout.addWidget(QLabel(env.translate("searchWindow.label.searchFor")))
        searchTextLayout.addWidget(self.searchEdit)

        numberLayout = QGridLayout()
        numberLayout.addWidget(self.lineLabel,0,0)
        numberLayout.addWidget(self.lineSpinBox,0,1)
        numberLayout.addWidget(self.indexLabel,1,0)
        numberLayout.addWidget(self.indexSpinBox,1,1)

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
        mainLayout.addWidget(self.showText)
        mainLayout.addWidget(self.searchRange)
        mainLayout.addLayout(numberLayout)
        mainLayout.addLayout(buttonLayout)
        mainLayout.setSizeConstraint(QLayout.SetFixedSize)

        self.setLayout(mainLayout)
        self.setWindowTitle(env.translate("searchWindow.title"))

    def searchButtonClicked(self):
        if bool(self.searchRange.checkState()):
            line = self.lineSpinBox.value()
            index = self.indexSpinBox.value()
        else:
            line = -1
            index = -1

        self.editWidget.findFirst(
            self.searchEdit.text(),
            self.regEx.checkState(),
            self.caseSensitive.checkState(),
            self.wholeWord.checkState(),
            self.wrap.checkState(),
            not bool(self.backward.checkState()),
            line,
            index,
            self.showText.checkState()
        )

    def searchRangeEnableUpdated(self):
        enabled =  bool(self.searchRange.checkState())
        self.lineLabel.setEnabled(enabled)
        self.indexLabel.setEnabled(enabled)
        self.lineSpinBox.setEnabled(enabled)
        self.indexSpinBox.setEnabled(enabled)

    def openWindow(self, editWidget):
        self.editWidget = editWidget
        self.searchRangeEnableUpdated()
        self.show()
        QApplication.setActiveWindow(self)
