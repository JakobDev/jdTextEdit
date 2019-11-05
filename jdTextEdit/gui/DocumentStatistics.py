from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QLayout
from jdTextEdit.Functions import getThemeIcon
import re

class DocumentStatistics(QWidget):
    def __init__(self, env):
        super().__init__()
        self.selectionLabel = QLabel(env.translate("documentStatistics.selection"))
        self.linesDocument = QLabel("0")
        self.linesSelection = QLabel("0")
        self.wordsDocument = QLabel("0")
        self.wordsSelection = QLabel("0")
        self.charactersSpacesDocument = QLabel("0")
        self.charactersSpacesSelection = QLabel("0")
        self.charactersNoSpacesDocument = QLabel("0")
        self.charactersNoSpacesSelection = QLabel("0")
        closeButton = QPushButton(env.translate("button.close"))

        closeButton.setIcon(getThemeIcon(env,"window-close"))
        closeButton.clicked.connect(self.close)

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(env.translate("documentStatistics.document")),0,1)
        gridLayout.addWidget(self.selectionLabel,0,2)
        gridLayout.addWidget(QLabel(env.translate("documentStatistics.lines")),1,0)
        gridLayout.addWidget(self.linesDocument,1,1)
        gridLayout.addWidget(self.linesSelection,1,2)
        gridLayout.addWidget(QLabel(env.translate("documentStatistics.words")),2,0)
        gridLayout.addWidget(self.wordsDocument,2,1)
        gridLayout.addWidget(self.wordsSelection,2,2)
        gridLayout.addWidget(QLabel(env.translate("documentStatistics.charactersSpaces")),3,0)
        gridLayout.addWidget(self.charactersSpacesDocument,3,1)
        gridLayout.addWidget(self.charactersSpacesSelection,3,2)
        gridLayout.addWidget(QLabel(env.translate("documentStatistics.charactersNoSpaces")),4,0)
        gridLayout.addWidget(self.charactersNoSpacesDocument,4,1)
        gridLayout.addWidget(self.charactersNoSpacesSelection,4,2)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(closeButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addLayout(buttonLayout)
        mainLayout.setSizeConstraint(QLayout.SetFixedSize)

        self.setLayout(mainLayout)
        self.setWindowTitle(env.translate("documentStatistics.title"))

    def openWindow(self, textEdit):
        documentString = textEdit.text()
        selectionString = textEdit.selectedText()

        isSelected = textEdit.hasSelectedText()
        self.selectionLabel.setEnabled(isSelected)
        self.linesSelection.setEnabled(isSelected)
        self.wordsSelection.setEnabled(isSelected)
        self.charactersSpacesSelection.setEnabled(isSelected)
        self.charactersNoSpacesSelection.setEnabled(isSelected)

        self.linesDocument.setText(str(len(documentString.split('\n'))))
        if isSelected:
            self.linesSelection.setText(str(len(selectionString.split('\n'))))
        else:
            self.linesSelection.setText("0")
        self.wordsDocument.setText(str(len(re.findall(r'\w+', documentString))))
        self.wordsSelection.setText(str(len(re.findall(r'\w+', selectionString))))
        self.charactersSpacesDocument.setText(str(len(documentString)))
        self.charactersSpacesSelection.setText(str(len(selectionString)))
        self.charactersNoSpacesDocument.setText(str(len(documentString.replace(" ","").replace("\n","").replace("\t",""))))
        self.charactersNoSpacesSelection.setText(str(len(selectionString.replace(" ","").replace("\n","").replace("\t",""))))

        self.show()
        QApplication.setActiveWindow(self)
