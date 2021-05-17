from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from jdTextEdit.api.SidebarWidgetBase import SidebarWidgetBase
from PyQt5.QtCore import Qt

class CharacterMapWidget(QTableWidget,SidebarWidgetBase):
    def __init__(self, env):
        super().__init__(256,2)
        self.env = env
        self.setHorizontalHeaderLabels((env.translate("sidebar.charactermap.decimal"),env.translate("sidebar.charactermap.character")))
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.verticalHeader().hide()
        for i in range(256):
            decimalItem = QTableWidgetItem(str(i))
            decimalItem.setFlags(decimalItem.flags() ^ Qt.ItemIsEditable)
            charItem = QTableWidgetItem(chr(i))
            charItem.setFlags(charItem.flags() ^ Qt.ItemIsEditable)
            self.setItem(i, 0,decimalItem)
            self.setItem(i, 1,charItem)
        self.cellClicked.connect(lambda row, column: env.mainWindow.getTextEditWidget().insertText(chr(row)))

    def getName(self) -> str:
        return self.env.translate("sidebar.charactermap")

    def getID(self) -> str:
        return "charactermap"
