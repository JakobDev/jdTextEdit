from PyQt5.QtWidgets import QTreeView,QFileSystemModel,QApplication

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
        file_path=self.model().filePath(signal)
        self.env.mainWindow.openFile(file_path)
