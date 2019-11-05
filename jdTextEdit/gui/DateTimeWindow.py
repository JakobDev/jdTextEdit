from PyQt5.QtWidgets import QApplication, QWidget, QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QHeaderView, QAbstractItemView, QRadioButton, QLineEdit, QLabel, QPushButton
from jdTextEdit.Functions import restoreWindowState
from PyQt5.QtCore import Qt
import time
import sys

class DateTimeWindow(QWidget):
    def __init__(self,env):
        super().__init__()
        self.env = env
        self.templates = []
        self.templates.append("%a %d %b %Y %H:%M:%S %Z")
        self.templates.append("%d.%m.%Y")
        self.templates.append("%H:%M:%S")
        self.templates.append("%d.%m.%Y %H:%M:%S")
        self.templates.append("%d-%m-%Y %H:%M:%S")
        self.templates.append("%a %b %d %H:%M:%S %Z %Y")
        self.templates.append("%a %b %d %H:%M:%S %Y")
        self.templates.append("%a %d %b %Y %H:%M:%S")
        self.templates.append("%d/%m/%Y")
        self.templates.append("%d/%m/%y")
        self.templates.append("%A %d %B %Y")
        self.templates.append("%A %B %d %Y")
        self.templates.append("%d-%m-%Y")
        self.templates.append("%d %B %Y")
        self.templates.append("%B %d %Y")
        self.templates.append("%A %b %d")
        self.templates.append("%H:%M")

        self.useTemplate = QRadioButton(env.translate("dateTimeWindow.radioButton.useTemplate"))
        self.templateTable = QTableWidget(0,1)
        self.useCustom = QRadioButton(env.translate("dateTimeWindow.radioButton.useCustom"))
        self.customEdit = QLineEdit()
        self.previewLabel = QLabel()
        okButton = QPushButton(env.translate("button.ok"))
        cancelButton = QPushButton(env.translate("button.cancel"))

        self.useTemplate.toggled.connect(self.updateCheckbox)
        self.useCustom.toggled.connect(self.updateCheckbox)
        self.customEdit.textChanged.connect(self.updatePreviewLabel)
        cancelButton.clicked.connect(lambda: self.close())
        okButton.clicked.connect(self.okButtonClicked)

        self.templateTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.templateTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.templateTable.horizontalHeader().hide()
        self.templateTable.verticalHeader().hide()
        self.templateTable.setCurrentCell(0,0)

        self.useTemplate.setChecked(True)
        self.customEdit.setText("%d/%m/%Y %H:%M:%S")

        customLayout = QHBoxLayout()
        customLayout.addWidget(self.customEdit)
        customLayout.addWidget(self.previewLabel)
    
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.useTemplate)
        mainLayout.addWidget(self.templateTable)
        mainLayout.addWidget(self.useCustom)
        mainLayout.addLayout(customLayout)
        mainLayout.addLayout(buttonLayout)
       
        self.setLayout(mainLayout)
        self.setWindowTitle(env.translate("dateTimeWindow.title"))
        restoreWindowState(self,env.windowState,"DateTimeWindow")
        self.updateTemplateList()

    def updateTemplateList(self):
        count = 0
        for i in self.templates:
            item = QTableWidgetItem(time.strftime(i))
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.templateTable.insertRow(count)
            self.templateTable.setItem(count,0,item)
            count += 1

    def updatePreviewLabel(self, text):
        self.previewLabel.setText(self.env.translate("dateTimeWindow.label.preview") % time.strftime(text))

    def updateCheckbox(self):
        if self.useTemplate.isChecked():
            self.templateTable.setEnabled(True)
            self.customEdit.setEnabled(False)
            self.previewLabel.setEnabled(False)
        else:
            self.templateTable.setEnabled(False)
            self.customEdit.setEnabled(True)
            self.previewLabel.setEnabled(True)

    def okButtonClicked(self):
        if self.useTemplate.isChecked():
            self.editWidget.insertText(time.strftime(self.templates[self.templateTable.currentRow()]))
        else:
            self.editWidget.insertText(time.strftime(self.customEdit.text()))
        self.editWidget.ensureCursorVisible()
        self.close()

    def openWindow(self, editWidget):
        self.editWidget = editWidget
        self.show()
        QApplication.setActiveWindow(self)
