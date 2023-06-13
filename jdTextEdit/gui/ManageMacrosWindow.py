from PyQt6.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton, QKeySequenceEdit, QHBoxLayout, QVBoxLayout
from jdTextEdit.Functions import restoreWindowState, showMessageBox
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
import json
import os


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class RemoveMacroButton(QPushButton):
    def __init__(self, text: str, pos: int, table: QTableWidget, macro: str):
        super().__init__(text)
        self.clicked.connect(lambda: table.removeRow(pos))
        self._macro = macro

    def getMacro(self) -> str:
        return self._macro


class ManageMacrosWindow(QWidget):
    def __init__(self, env: "Environment"):
        super().__init__()
        self.env = env

        self.macroTable = QTableWidget(1, 3)
        okButton = QPushButton(QCoreApplication.translate("ManageMacrosWindow", "OK"))
        cancelButton = QPushButton(QCoreApplication.translate("ManageMacrosWindow", "Cancel"))

        self.macroTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.macroTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.macroTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.macroTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.macroTable.horizontalHeader().hide()
        self.macroTable.verticalHeader().hide()

        okButton.clicked.connect(self.okButtonClicked)
        cancelButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        if env.settings.get("swapOkCancel"):
            buttonLayout.addWidget(okButton)
            buttonLayout.addWidget(cancelButton)
        else:
            buttonLayout.addWidget(cancelButton)
            buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.macroTable)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(QCoreApplication.translate("ManageMacrosWindow", "Manage macros"))
        self.resize(700, 500)
        restoreWindowState(self, env.windowState, "ManageMacrosWindow")

    def okButtonClicked(self):
        self.env.macroList.clear()
        for i in range(self.macroTable.rowCount()):
            macro = {}
            macro["name"] = self.macroTable.item(i, 0).text()
            macro["shortcut"] = self.macroTable.cellWidget(i, 1).keySequence().toString()
            macro["macro"] = self.macroTable.cellWidget(i, 2).getMacro()
            self.env.macroList.append(macro)
        self.env.mainWindow.updateMacroMenu()
        with open(os.path.join(self.env.dataDir, "macros.json"), "w", encoding="utf-8") as f:
            json.dump(self.env.macroList, f, ensure_ascii=False, indent=4)
        self.close()

    def openWindow(self):
        if len(self.env.macroList) == 0:
            showMessageBox(QCoreApplication.translate("ManageMacrosWindow", "No macros available"), QCoreApplication.translate("ManageMacrosWindow", "There are currently no macros available. You have to record some before you can manage them."))
            return

        while self.macroTable.rowCount() > 0:
            self.macroTable.removeRow(0)

        for count, i in enumerate(self.env.macroList):
            self.macroTable.insertRow(count)
            self.macroTable.setItem(count, 0, QTableWidgetItem(i["name"]))
            shortcutEdit = QKeySequenceEdit(i["shortcut"])
            shortcutEdit.setClearButtonEnabled(True)
            self.macroTable.setCellWidget(count, 1, shortcutEdit)
            self.macroTable.setCellWidget(count, 2, RemoveMacroButton(QCoreApplication.translate("ManageMacrosWindow", "Remove macro"), count, self.macroTable, i["macro"]))

        self.show()
        QApplication.setActiveWindow(self)
