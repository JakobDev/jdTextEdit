from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton, QKeySequenceEdit, QHBoxLayout, QVBoxLayout, QGridLayout
from jdTextEdit.Functions import restoreWindowState, showMessageBox
import json
import os

class ClearShortcutButton(QPushButton):
    def __init__(self,text,pos,table):
        super().__init__(text)
        self.clicked.connect(lambda: table.cellWidget(pos,1).setKeySequence(""))

class RemoveMacroButton(QPushButton):
    def __init__(self,text,pos,table,macro):
        super().__init__(text)
        self.clicked.connect(lambda: table.removeRow(table.currentRow()))
        self.macro = macro
    
    def getMacro(self):
        return self.macro


class ManageMacrosWindow(QWidget):
    def __init__(self, env):
        super().__init__()
        self.env = env
        self.macroTable = QTableWidget(1,4)
        okButton = QPushButton(env.translate("button.ok"))
        cancelButton = QPushButton(env.translate("button.cancel"))

        self.macroTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.macroTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.macroTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.macroTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.macroTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.macroTable.horizontalHeader().hide()
        self.macroTable.verticalHeader().hide()

        okButton.clicked.connect(self.okButtonClicked)
        cancelButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.macroTable)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(self.env.translate("manageMacrosWindow.title"))
        self.resize(700, 500)
        restoreWindowState(self,env.windowState,"ManageMacrosWindow")

    def okButtonClicked(self):
        self.env.macroList.clear()
        for i in range(self.macroTable.rowCount()):
            macro = {}
            macro["name"] = self.macroTable.item(i,0).text()
            macro["shortcut"] = self.macroTable.cellWidget(i,1).keySequence().toString()
            macro["macro"] = self.macroTable.cellWidget(i,3).getMacro()
            self.env.macroList.append(macro)
        self.env.mainWindow.updateMacroMenu()
        with open(os.path.join(self.env.dataDir,"macros.json"), 'w', encoding='utf-8') as f:
            json.dump(self.env.macroList, f, ensure_ascii=False, indent=4)
        self.close()

    def openWindow(self):
        if len(self.env.macroList) == 0:
            showMessageBox(self.env.translate("manageMacrosWindow.noMacros.title"),self.env.translate("manageMacrosWindow.noMacros.text"))
            return
        while (self.macroTable.rowCount() > 0):
            self.macroTable.removeRow(0)
        for count, i in enumerate(self.env.macroList):
            self.macroTable.insertRow(count)
            self.macroTable.setItem(count,0,QTableWidgetItem(i["name"]))
            self.macroTable.setCellWidget(count,1,QKeySequenceEdit(i["shortcut"]))
            self.macroTable.setCellWidget(count,2,ClearShortcutButton(self.env.translate("manageMacrosWindow.button.clearShortcut"),count,self.macroTable))
            self.macroTable.setCellWidget(count,3,RemoveMacroButton(self.env.translate("manageMacrosWindow.button.removeMacro"),count,self.macroTable,i["macro"]))    
        self.show()
        QApplication.setActiveWindow(self)
