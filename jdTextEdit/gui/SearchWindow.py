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
        self.lineSpinBox = QSpinBox()
        self.indexSpinBox = QSpinBox()
        self.closeButton = QPushButton(env.translate("button.close"))
        self.searchButton = QPushButton(env.translate("searchWindow.button.search"))

        self.wrap.setChecked(True)
        self.showText.setChecked(True)

        self.lineSpinBox.setRange(-1,2147483647)
        self.indexSpinBox.setRange(-1,2147483647)

        self.lineSpinBox.setValue(-1)
        self.indexSpinBox.setValue(-1)

        self.closeButton.setIcon(getThemeIcon(env,"window-close"))
        self.searchButton.setIcon(getThemeIcon(env,"edit-find"))

        self.closeButton.clicked.connect(self.close)
        self.searchButton.clicked.connect(self.searchButtonClicked)

        searchTextLayout = QHBoxLayout()
        searchTextLayout.addWidget(QLabel(env.translate("searchWindow.label.searchFor")))
        searchTextLayout.addWidget(self.searchEdit)
        
        numberLayout = QGridLayout()
        numberLayout.addWidget(QLabel(env.translate("searchWindow.label.searchLine")),0,0)
        numberLayout.addWidget(self.lineSpinBox,0,1)
        numberLayout.addWidget(QLabel(env.translate("searchWindow.label.searchColumn")),1,0)
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
        mainLayout.addLayout(numberLayout)
        mainLayout.addLayout(buttonLayout)
        mainLayout.setSizeConstraint(QLayout.SetFixedSize)

        self.setLayout(mainLayout)
        self.setWindowTitle(env.translate("searchWindow.title"))

    def searchButtonClicked(self):
        self.editWidget.findFirst(self.searchEdit.text(),self.regEx.checkState(),self.caseSensitive.checkState(),self.wholeWord.checkState(),self.wrap.checkState(),not bool(self.backward.checkState()),self.lineSpinBox.value(),self.indexSpinBox.value(),self.showText.checkState())

    def openWindow(self, editWidget):
        self.editWidget = editWidget
        self.show()
        QApplication.setActiveWindow(self)
