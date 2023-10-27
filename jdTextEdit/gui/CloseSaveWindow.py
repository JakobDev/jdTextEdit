from PyQt6.QtWidgets import QApplication, QDialog, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QLayout
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
import sys


if TYPE_CHECKING:
    from jdTextEdit.gui.EditTabWidget import EditTabWidget
    from jdTextEdit.Environment import Environment


class CloseSaveWindow(QDialog):
    def __init__(self, env: "Environment"):
        super().__init__()
        self.env = env

        noCloseButton = QPushButton(QCoreApplication.translate("CloseSaveWindow", "Close without Saving"))
        cancelButton = QPushButton(QCoreApplication.translate("CloseSaveWindow", "Cancel"))
        self.saveButton = QPushButton()
        self.text = QLabel()

        noCloseButton.clicked.connect(self.closeFile)
        cancelButton.clicked.connect(self.close)
        self.saveButton.clicked.connect(self.saveFile)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.saveButton)
        buttonLayout.addWidget(noCloseButton)
        buttonLayout.addWidget(cancelButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.text)
        mainLayout.addLayout(buttonLayout)
        mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.setLayout(mainLayout)

    def closeFile(self):
        self.tabWidget.removeTab(self.tabid)
        if self.tabWidget.count() == 0:
            sys.exit(0)
        self.close()

    def saveFile(self):
        editWidget = self.tabWidget.editWidget(self.tabid)
        if editWidget.getFilePath() == "":
            path = QFileDialog.getSaveFileName(self, QCoreApplication.translate("CloseSaveWindow", "Save as ..."), None, self.env.fileNameFilters)[0]
            if path == "":
                return
        else:
            path = editWidget.getFilePath()
        editWidget.setFilePath(path)
        self.tabWidget.getSplitViewWidget().getMainWindow().saveFile(editWidget, path)
        self.closeFile()

    def openWindow(self, tabid: int, tabWidget: "EditTabWidget"):
        self.tabid = tabid
        self.tabWidget = tabWidget
        filename = self.tabWidget.tabText(tabid)
        self.text.setText(QCoreApplication.translate("CloseSaveWindow", "{{path}} has been edited. Do you want to save it?").replace("{{path}}", filename))
        self.setWindowTitle(QCoreApplication.translate("CloseSaveWindow", "Save {{path}}").replace("{{path}}", filename))
        if self.tabWidget.editWidget(self.tabid).getFilePath() == "":
            self.saveButton.setText(QCoreApplication.translate("CloseSaveWindow", "Save as ..."))
        else:
            self.saveButton.setText(QCoreApplication.translate("CloseSaveWindow", "Save"))
        self.exec()
        QApplication.setActiveWindow(self)
