from jdTextEdit.api.SidebarWidgetBase import SidebarWidgetBase
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import QTreeView
import os

class FileTreeWidget(QTreeView,SidebarWidgetBase):
    def __init__(self, env):
        QTreeView.__init__(self)
        self.env = env
        model = QFileSystemModel()
        model.setRootPath('/')
        self.setModel(model)
        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(3)
        self.doubleClicked.connect(self.fileOpen)

    def fileOpen(self, signal):
        path=self.model().filePath(signal)
        if os.path.isfile(path):
            self.env.mainWindow.openFile(path)

    def getName(self) -> str:
        return self.env.translate("sidebar.files")

    def getID(self) -> str:
        return "files"
