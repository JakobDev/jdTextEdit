from PyQt6.QtWidgets import QDialog, QListWidget, QVBoxLayout, QHBoxLayout, QInputDialog, QMessageBox, QRadioButton, QLineEdit, QLabel, QPushButton
from jdTextEdit.Functions import restoreWindowState, readJsonFile
from typing import Optional, TYPE_CHECKING
from PyQt6.QtCore import QCoreApplication
import time
import json
import os


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment
    from jdTextEdit.gui.CodeEdit import CodeEdit


class DateTimeWindow(QDialog):
    def __init__(self, env: "Environment"):
        super().__init__()
        self.env = env

        defaultTemplates = [
            "%a %d %b %Y %H:%M:%S %Z",
            "%d.%m.%Y",
            "%H:%M:%S",
            "%d.%m.%Y %H:%M:%S",
            "%d-%m-%Y %H:%M:%S",
            "%a %b %d %H:%M:%S %Z %Y",
            "%a %b %d %H:%M:%S %Y",
            "%a %d %b %Y %H:%M:%S",
            "%d/%m/%Y",
            "%d/%m/%y",
            "%A %d %B %Y",
            "%A %B %d %Y",
            "%d-%m-%Y",
            "%d %B %Y",
            "%B %d %Y",
            "%A %b %d",
            "%H:%M"
        ]

        self.templates: list[str] = readJsonFile(os.path.join(self.env.dataDir, "dateTimeFormats.json"), defaultTemplates)

        self.useTemplate = QRadioButton(QCoreApplication.translate("DateTimeWindow", "Use the selected format"))
        self.templateList = QListWidget()
        self.templateAddButton = QPushButton(QCoreApplication.translate("DateTimeWindow", "Add"))
        self.templateEditButton = QPushButton(QCoreApplication.translate("DateTimeWindow", "Edit"))
        self.templateRemoveButton = QPushButton(QCoreApplication.translate("DateTimeWindow", "Remove"))
        self.useCustom = QRadioButton(QCoreApplication.translate("DateTimeWindow", "Use custom format"))
        self.customEdit = QLineEdit()
        self.previewLabel = QLabel()
        self.okButton = QPushButton(QCoreApplication.translate("DateTimeWindow", "OK"))
        cancelButton = QPushButton(QCoreApplication.translate("DateTimeWindow", "Cancel"))

        self.useTemplate.toggled.connect(self.updateCheckbox)
        self.templateList.itemSelectionChanged.connect(self.updateTemplateButtons)
        self.templateAddButton.clicked.connect(lambda: self.addEditTemplateClicked(None))
        self.templateEditButton.clicked.connect(lambda: self.addEditTemplateClicked(self.templateList.currentRow()))
        self.templateRemoveButton.clicked.connect(self.removeTemplateClicked)
        self.useCustom.toggled.connect(self.updateCheckbox)
        self.customEdit.textChanged.connect(self.updatePreviewLabel)
        cancelButton.clicked.connect(lambda: self.close())
        self.okButton.clicked.connect(self.okButtonClicked)

        self.useTemplate.setChecked(True)
        self.customEdit.setText("%d/%m/%Y %H:%M:%S")

        templateButtonLayout = QHBoxLayout()
        templateButtonLayout.addWidget(self.templateAddButton)
        templateButtonLayout.addWidget(self.templateEditButton)
        templateButtonLayout.addWidget(self.templateRemoveButton)
        templateButtonLayout.setSpacing(0)
        templateButtonLayout.setContentsMargins(0, 0, 0, 0)

        templateLayout = QVBoxLayout()
        templateLayout.addWidget(self.templateList)
        templateLayout.addLayout(templateButtonLayout)
        templateLayout.setSpacing(0)
        templateLayout.setContentsMargins(0, 0, 0, 0)

        customLayout = QHBoxLayout()
        customLayout.addWidget(self.customEdit)
        customLayout.addWidget(self.previewLabel)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        if env.settings.get("swapOkCancel"):
            buttonLayout.addWidget(self.okButton)
            buttonLayout.addWidget(cancelButton)
        else:
            buttonLayout.addWidget(cancelButton)
            buttonLayout.addWidget(self.okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.useTemplate)
        mainLayout.addLayout(templateLayout)
        mainLayout.addWidget(self.useCustom)
        mainLayout.addLayout(customLayout)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(QCoreApplication.translate("DateTimeWindow", "Insert Date and Time"))
        restoreWindowState(self,env.windowState, "DateTimeWindow")
        self.updateTemplateList()

    def updateTemplateList(self):
        self.templateList.clear()
        for i in self.templates:
            self.templateList.addItem(time.strftime(i))
        self.updateTemplateButtons()

    def updatePreviewLabel(self, text):
        try:
            self.previewLabel.setText(QCoreApplication.translate("DateTimeWindow", "Preview: {{preview}}").replace("{{preview}}", time.strftime(text)))
        except ValueError:
            self.previewLabel.setText(QCoreApplication.translate("DateTimeWindow", "Invalid"))

    def updateTemplateButtons(self):
        enabled = self.useTemplate.isChecked() and self.templateList.currentRow() != -1
        self.templateEditButton.setEnabled(enabled)
        self.templateRemoveButton.setEnabled(enabled)

        self.okButton.setEnabled(not (self.useTemplate.isChecked() and self.templateList.currentRow() == -1))

    def updateCheckbox(self):
        if self.useTemplate.isChecked():
            self.templateList.setEnabled(True)
            self.templateAddButton.setEnabled(True)
            self.customEdit.setEnabled(False)
            self.previewLabel.setEnabled(False)
        else:
            self.templateList.setEnabled(False)
            self.templateAddButton.setEnabled(False)
            self.customEdit.setEnabled(True)
            self.previewLabel.setEnabled(True)
        self.updateTemplateButtons()

    def saveTemplates(self):
        with open(os.path.join(self.env.dataDir, "dateTimeFormats.json"), "w", encoding="utf-8") as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=4)

    def addEditTemplateClicked(self, position: Optional[int]):
        text = QInputDialog.getText(self, QCoreApplication.translate("DateTimeWindow", "Enter format"), QCoreApplication.translate("DateTimeWindow", "Please enter a format"), text=(lambda: self.templates[position] if position is not None else "")())[0]

        if text.strip() == "":
            return

        try:
            time.strftime(text)
        except ValueError:
            QMessageBox.critical(self, QCoreApplication.translate("DateTimeWindow", "Invalid format"), QCoreApplication.translate("DateTimeWindow", "This format is invalid"))
            return

        if position is None:
            self.templates.append(text)
        else:
            self.templates[position] = text

        self.updateTemplateList()
        self.saveTemplates()

    def removeTemplateClicked(self):
        del self.templates[self.templateList.currentRow()]
        self.updateTemplateList()
        self.saveTemplates()

    def okButtonClicked(self):
        if self.useTemplate.isChecked():
            self.editWidget.insertText(time.strftime(self.templates[self.templateList.currentRow()]))
        else:
            self.editWidget.insertText(time.strftime(self.customEdit.text()))
        self.editWidget.ensureCursorVisible()
        self.close()

    def openWindow(self, editWidget: "CodeEdit"):
        self.editWidget = editWidget
        self.updateTemplateList()
        self.exec()
