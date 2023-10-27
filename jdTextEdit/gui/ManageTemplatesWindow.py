from PyQt6.QtWidgets import QDialog, QListWidget, QPushButton, QMessageBox, QInputDialog, QFileDialog, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
import shutil
import sys
import os


if TYPE_CHECKING:
    from jdTextEdit.gui.MainWindow import MainWindow
    from jdTextEdit.Environment import Environment


class ManageTemplatesWindow(QDialog):
    def __init__(self, env: "Environment"):
        super().__init__()
        self._env = env

        self._templateList = QListWidget()
        self._deleteButton = QPushButton(QCoreApplication.translate("ManageTemplatesWindow", "Delete"))
        self._renameButton = QPushButton(QCoreApplication.translate("ManageTemplatesWindow", "Rename"))
        self._exportButton = QPushButton(QCoreApplication.translate("ManageTemplatesWindow", "Export"))
        closeButton = QPushButton(QCoreApplication.translate("ManageTemplatesWindow", "Close"))

        self._deleteButton.clicked.connect(self._deleteButtonClicked)
        self._renameButton.clicked.connect(self._renameButtonClicked)
        self._exportButton.clicked.connect(self._exportButtonClicked)
        closeButton.clicked.connect(self.close)

        self._templateList.itemSelectionChanged.connect(self._updateButtonsEnabled)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self._deleteButton)
        buttonLayout.addWidget(self._renameButton)
        buttonLayout.addWidget(self._exportButton)
        buttonLayout.addWidget(closeButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self._templateList)
        mainLayout.addLayout(buttonLayout)

        self.setWindowTitle(QCoreApplication.translate("ManageTemplatesWindow", "Manage templates"))
        self.setLayout(mainLayout)

    def _updateButtonsEnabled(self):
        enabled = self._templateList.currentRow() != -1
        self._deleteButton.setEnabled(enabled)
        self._renameButton.setEnabled(enabled)
        self._exportButton.setEnabled(enabled)

    def _updateTemplateList(self):
        self._templateList.clear()
        if os.path.isdir(os.path.join(self._env.dataDir, "templates")):
            for i in os.listdir(os.path.join(self._env.dataDir, "templates")):
                self._templateList.addItem(i)
        self._updateButtonsEnabled()

    def _deleteButtonClicked(self):
        currentName = self._templateList.currentItem().text()

        if QMessageBox.question(self, QCoreApplication.translate("ManageTemplatesWindow", "Delete {{name}}").replace("{{name}}", currentName), QCoreApplication.translate("ManageTemplatesWindow", "Are you sure you want to delete {{name}}?").replace("{{name}}", currentName), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return

        try:
            os.remove(os.path.join(self._env.dataDir, "templates", currentName))
        except Exception as ex:
            self._env.logger.exception(ex)
            QMessageBox.critical(self, QCoreApplication.translate("ManageTemplatesWindow", "Error"), QCoreApplication.translate("ManageTemplatesWindow", "A error occurred while deleting"))
            return

        self._updateTemplateList()
        self._env.updateTemplates()
        self._mainWindow.updateTemplateMenu()

    def _renameButtonClicked(self):
        oldName = self._templateList.currentItem().text()

        newName = QInputDialog.getText(self, QCoreApplication.translate("ManageTemplatesWindow", "Enter name"), QCoreApplication.translate("ManageTemplatesWindow", "Please enter the new name"), text=oldName)[0]

        if newName == "":
            return

        if os.path.exists(os.path.join(self._env.dataDir, "templates", newName)):
            QMessageBox.critical(self, QCoreApplication.translate("ManageTemplatesWindow", "Name exists"), QCoreApplication.translate("ManageTemplatesWindow", "There is already a template with this name"))
            return

        try:
            os.rename(os.path.join(self._env.dataDir, "templates", oldName), os.path.join(self._env.dataDir, "templates", newName))
        except Exception as ex:
            self._env.logger.exception(ex)
            QMessageBox.critical(self, QCoreApplication.translate("ManageTemplatesWindow", "Error"), QCoreApplication.translate("ManageTemplatesWindow", "A error occurred while renaming"))
            return

        self._updateTemplateList()
        self._env.updateTemplates()
        self._mainWindow.updateTemplateMenu()

    def _exportButtonClicked(self) -> None:
        exportPath = QFileDialog.getSaveFileName(self, directory=self._templateList.currentItem().text())[0]

        if exportPath == "":
            return

        templatePath = os.path.join(self._env.dataDir, "templates", self._templateList.currentItem().text())
        try:
            shutil.copyfile(templatePath, exportPath)
        except Exception as ex:
            self._env.logger.exception(ex)
            QMessageBox.critical(self, QCoreApplication.translate("ManageTemplatesWindow", "Error"), QCoreApplication.translate("ManageTemplatesWindow", "A error occurred while exporting"))

    def openWindow(self, mainWindow: "MainWindow") -> None:
        self._mainWindow = mainWindow
        self._updateTemplateList()
        self.exec()
