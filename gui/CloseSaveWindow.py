from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QLayout
import sys

class CloseSaveWindow(QWidget):
    def __init__(self,env):
        super().__init__()
        self.env = env
        noCloseButton = QPushButton(env.translate("closeSaveWindow.button.noSave"))
        cancelButton = QPushButton(env.translate("button.cancel"))
        self.saveButton = QPushButton()
        self.text = QLabel()  

        noCloseButton.clicked.connect(self.closeFile)
        cancelButton.clicked.connect(self.close)
        self.saveButton.clicked.connect(self.saveFile)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(noCloseButton)
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(self.saveButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.text)
        mainLayout.addLayout(buttonLayout)
        mainLayout.setSizeConstraint(QLayout.SetFixedSize)

        self.setLayout(mainLayout)

    def closeFile(self):
        del self.tabWidget.tabs[self.tabid]
        self.tabWidget.removeTab(self.tabid)
        if len(self.tabWidget.tabs) == 0:
            sys.exit(0)
        self.close()

    def saveFile(self):
        if self.tabWidget.tabs[self.tabid][1] == "":
            pickedPath = QFileDialog.getSaveFileName(self,"Pick File")
            if pickedPath[0]:
                path = pickedPath[0]
            else:
                self.closeFile()
        else:
            path = self.tabWidget.tabs[self.tabid][1]
        f = open(path,"w")
        f.write(self.fileContent)
        f.close()
        self.closeFile()

    def openWindow(self, tabid):
        self.tabid = tabid
        self.tabWidget = self.env.mainWindow.tabWidget
        self.fileContent = self.env.mainWindow.getTextEditWidget().text()
        filename = self.tabWidget.tabText(tabid)
        self.text.setText(self.env.translate("closeSaveWindow.text") % filename)
        self.setWindowTitle(self.env.translate("closeSaveWindow.title") % filename)
        if self.tabWidget.tabs[self.tabid][1] == "":
            self.saveButton.setText(self.env.translate("closeSaveWindow.button.saveAs"))
        else:
            self.saveButton.setText(self.env.translate("closeSaveWindow.button.save"))
        self.show()
        self.setFocus()
           
