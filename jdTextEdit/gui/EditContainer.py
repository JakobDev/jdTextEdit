from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from jdTextEdit.gui.CodeEdit import CodeEdit
from PyQt5.QtCore import QFileSystemWatcher
from jdTextEdit.gui.BannerWidgets.FileChangedBanner import FileChangedBanner

class EditContainer(QWidget):
    def __init__(self,env):
        super().__init__()
        self.env = env
        self.codeWidget = CodeEdit(env,isNew=True)
        self.currentPath = self.codeWidget.getFilePath()
        self.codeWidget.pathChanged.connect(self.newPath)

        self.fileChangedWidget = FileChangedBanner(self.env,self)

        self.fileWatcher = QFileSystemWatcher()
        self.fileWatcher.fileChanged.connect(self.fileChanged)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.codeWidget)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)

        self.setLayout(self.mainLayout)

        #mainLayout.addWidget(QLabel("Hallo"),-1)

    def getCodeEditWidget(self):
        return self.codeWidget

    def showBanner(self, widget):
        self.mainLayout.insertWidget(0,widget)
        widget.show()

    def removeBanner(self, widget):
        widget.close()
        self.mainLayout.removeWidget(widget)

    def clearBanner(self):
        for i in reversed(range(self.mainLayout.count())):
            self.mainLayout.itemAt(i).widget().setParent(None)
        self.mainLayout.addWidget(self.codeWidget)

    def newPath(self,path):
        if len(self.fileWatcher.files()) != 0:
            self.fileWatcher.removePath(self.currentPath)
        self.currentPath = path
        if path != "":
            self.fileWatcher.addPath(path)

    def fileChanged(self, path):
        self.fileWatcher.addPath(path)
        if self.env.settings.showFileChangedBanner:
            self.showBanner(self.fileChangedWidget)
