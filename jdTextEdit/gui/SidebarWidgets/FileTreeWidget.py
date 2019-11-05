from PyQt5.QtWidgets import QTreeView,QFileSystemModel,QApplication
from jdTextEdit.Functions import showMessageBox
import os

class FileTreeWidget(QTreeView):
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
