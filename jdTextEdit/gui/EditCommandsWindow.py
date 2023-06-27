from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QTableWidget, QAbstractItemView, QPushButton, QCheckBox, QKeySequenceEdit, QTableWidgetItem, QHBoxLayout, QVBoxLayout, QHeaderView
from jdTextEdit.Functions import restoreWindowState
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
import json
import os


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class EditCommandsWindow(QWidget):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env

        self.commandsTable = QTableWidget(0, 4)
        addButton = QPushButton(QCoreApplication.translate("EditCommandsWindow", "Add"))
        self.removeButton = QPushButton(QCoreApplication.translate("EditCommandsWindow", "Remove"))
        okButton = QPushButton(QCoreApplication.translate("EditCommandsWindow", "OK"))
        cancelButton = QPushButton(QCoreApplication.translate("EditCommandsWindow", "Cancel"))

        self.commandsTable.setHorizontalHeaderLabels((QCoreApplication.translate("EditCommandsWindow", "Text"), QCoreApplication.translate("EditCommandsWindow", "Command"), QCoreApplication.translate("EditCommandsWindow", "Terminal"), QCoreApplication.translate("EditCommandsWindow", "Shortcut")))
        self.commandsTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.commandsTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.commandsTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.commandsTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.commandsTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.commandsTable.itemSelectionChanged.connect(self.updateRemoveButtonEnabled)
        addButton.clicked.connect(self.newRow)
        self.removeButton.clicked.connect(lambda: self.commandsTable.removeRow(self.commandsTable.currentRow()))
        okButton.clicked.connect(self.okButtonClicked)
        cancelButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(addButton)
        buttonLayout.addWidget(self.removeButton)
        buttonLayout.addStretch(1)
        if env.settings.get("swapOkCancel"):
            buttonLayout.addWidget(okButton)
            buttonLayout.addWidget(cancelButton)
        else:
            buttonLayout.addWidget(cancelButton)
            buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("%url% - " + QCoreApplication.translate("EditCommandsWindow", "Full URL of the currently active file")))
        mainLayout.addWidget(QLabel("%path% - " + QCoreApplication.translate("EditCommandsWindow", "Full path of the currently active file")))
        mainLayout.addWidget(QLabel("%directory% - " + QCoreApplication.translate("EditCommandsWindow", "Directory of the currently active file")))
        mainLayout.addWidget(QLabel("%filename% - " + QCoreApplication.translate("EditCommandsWindow", "Name of the currently active file")))
        mainLayout.addWidget(QLabel("%selection% - " + QCoreApplication.translate("EditCommandsWindow", "Currently selected text")))
        mainLayout.addWidget(self.commandsTable)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(QCoreApplication.translate("EditCommandsWindow", "Edit Commands"))
        restoreWindowState(self, env.windowState, "EditCommandsWindow")

    def openWindow(self) -> None:
        while self.commandsTable.rowCount() > 0:
            self.commandsTable.removeRow(0)

        count = 0
        for i in self.env.commands:
            self.commandsTable.insertRow(count)
            self.commandsTable.setItem(count, 0, QTableWidgetItem(i[0]))
            self.commandsTable.setItem(count, 1, QTableWidgetItem(i[1]))
            checkbox = QCheckBox()
            checkbox.setChecked(i[2])
            self.commandsTable.setCellWidget(count, 2, checkbox)
            shortcutEdit = QKeySequenceEdit()
            shortcutEdit.setClearButtonEnabled(True)

            if len(i) == 4:
                shortcutEdit.setKeySequence(i[3])

            self.commandsTable.setCellWidget(count, 3, shortcutEdit)
            count += 1

        self.updateRemoveButtonEnabled()
        self.show()
        QApplication.setActiveWindow(self)

    def newRow(self) -> None:
        shortcutEdit = QKeySequenceEdit()
        shortcutEdit.setClearButtonEnabled(True)
        self.commandsTable.insertRow(self.commandsTable.rowCount())
        self.commandsTable.setCellWidget(self.commandsTable.rowCount() - 1, 2, QCheckBox())
        self.commandsTable.setCellWidget(self.commandsTable.rowCount() - 1, 3, shortcutEdit)

    def updateRemoveButtonEnabled(self) -> None:
        self.removeButton.setEnabled(len(self.commandsTable.selectedIndexes()) > 0)

    def okButtonClicked(self) -> None:
        self.env.commands.clear()
        for i in range(self.commandsTable.rowCount()):
            try:
                name = self.commandsTable.item(i, 0).text()
                command = self.commandsTable.item(i, 1).text()
                terminal = self.commandsTable.cellWidget(i, 2).isChecked()
                shortcut = self.commandsTable.cellWidget(i, 3).keySequence().toString()
                if name != "":
                    self.env.commands.append([name, command, terminal, shortcut])
            except Exception:
                pass

        with open(os.path.join(self.env.dataDir, "commands.json"), "w", encoding="utf-8") as f:
            json.dump(self.env.commands, f, ensure_ascii=False, indent=4)

        self.env.mainWindow.updateExecuteMenu()
        self.close()
