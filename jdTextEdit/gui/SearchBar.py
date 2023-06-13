from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.gui.EditContainer import EditContainer
    from jdTextEdit.Environment import Environment


class SearchBar(QWidget):
    def __init__(self, env: "Environment", container: "EditContainer"):
        super().__init__()
        self.container = container
        self.textBox = QLineEdit()
        closeButton = QPushButton("x")
        nextButton = QPushButton("↓")
        firstButton = QPushButton("↑")

        closeButton.clicked.connect(self.container.hideSearchBar)
        self.textBox.textChanged.connect(self._searchTextChanged)
        nextButton.clicked.connect(lambda: self.container.getCodeEditWidget().findNext())
        firstButton.clicked.connect(self._searchTextChanged)

        nextButton.setToolTip(QCoreApplication.translate("SearchBar", "Jump to next match"))
        firstButton.setToolTip(QCoreApplication.translate("SearchBar", "Jump to first match"))

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(closeButton)
        mainLayout.addWidget(QLabel(QCoreApplication.translate("SearchBar", "Search:")))
        mainLayout.addWidget(self.textBox)
        mainLayout.addWidget(nextButton)
        mainLayout.addWidget(firstButton)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(mainLayout)

    def _searchTextChanged(self) -> None:
        self.container.getCodeEditWidget().findFirst(self.textBox.text(), False, False, False, True, line=0, index=0)
