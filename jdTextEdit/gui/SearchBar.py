from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout
from jdTextEdit.Enviroment import Enviroment

class SearchBar(QWidget):
    def __init__(self,env: Enviroment,container):
        super().__init__()
        self.container = container
        self.textBox = QLineEdit()
        closeButton = QPushButton("x")
        nextButton = QPushButton("↓")
        firstButton = QPushButton("↑")

        closeButton.clicked.connect(self.container.hideSearchBar)
        self.textBox.textChanged.connect(self.searchTextChanged)
        nextButton.clicked.connect(lambda: self.container.getCodeEditWidget().findNext())
        firstButton.clicked.connect(self.searchTextChanged)

        nextButton.setToolTip(env.translate("searchBar.tooltip.findNext"))
        firstButton.setToolTip(env.translate("searchBar.tooltip.findFirst"))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(closeButton)
        mainLayout.addWidget(QLabel(env.translate("searchBar.label.search")))
        mainLayout.addWidget(self.textBox)
        mainLayout.addWidget(nextButton)
        mainLayout.addWidget(firstButton)
        mainLayout.setContentsMargins(0,0,0,0)

        self.setLayout(mainLayout)

    def searchTextChanged(self):
        self.container.getCodeEditWidget().findFirst(self.textBox.text(),False,False,False,True,line=0,index=0)
