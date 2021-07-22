from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from jdTextEdit.gui.CodeEdit import CodeEdit
from PyQt6.QtCore import QFileSystemWatcher
from jdTextEdit.gui.BannerWidgets.FileChangedBanner import FileChangedBanner
from jdTextEdit.gui.BannerWidgets.FileDeletedBanner import FileDeletedBanner
from jdTextEdit.gui.SearchBar import SearchBar
import os

class EditContainer(QWidget):
    def __init__(self,env,tabWidget):
        super().__init__()
        self.env = env
        self.tabWidget = tabWidget
        self.codeWidget = CodeEdit(env,isNew=True,container=self)
        self.currentPath = self.codeWidget.getFilePath()
        self.codeWidget.pathChanged.connect(self.newPath)
        self.searchBar = None

        self.readOnlyLabel = QLabel("Test")
        self.readOnlyLabel.hide()
        self.fileChangedWidget = FileChangedBanner(self.env,self)
        self.fileDeletedWidget = FileDeletedBanner(self.env,self)

        self.fileWatcher = QFileSystemWatcher()
        self.fileWatcher.fileChanged.connect(self.fileChanged)

        self.mainLayout = QVBoxLayout()
        #self.mainLayout.addWidget(self.readOnlyLabel)
        self.mainLayout.addWidget(self.codeWidget)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)

        self.setLayout(self.mainLayout)

        #mainLayout.addWidget(QLabel("Hallo"),-1)

    def getCodeEditWidget(self) -> CodeEdit:
        """
        Retruns the edit widget
        :return: edit widget
        """
        return self.codeWidget

    def getTabWidget(self):
        """
        Returns the Tab Widget of the Container
        :return: tab widget
        """
        return self.tabWidget

    def showBanner(self, widget: QWidget):
        self.mainLayout.insertWidget(0,widget)
        widget.show()

    def removeBanner(self, widget):
        widget.close()
        self.mainLayout.removeWidget(widget)

    def clearBanner(self):
        for i in reversed(range(self.mainLayout.count())):
            self.mainLayout.itemAt(i).widget().setParent(None)
        #self.mainLayout.addWidget(self.readOnlyLabel)
        self.mainLayout.addWidget(self.codeWidget)

    def newPath(self,path):
        if len(self.fileWatcher.files()) != 0:
            self.fileWatcher.removePath(self.currentPath)
        self.currentPath = path
        if path != "":
            self.fileWatcher.addPath(path)

    def fileChanged(self, path: str):
        if os.path.exists(path):
            self.fileWatcher.addPath(path)
            self.showFileChangedBanner()
        else:
            self.showFileDeletedBanner()

    def showFileChangedBanner(self):
        if self.env.settings.showFileChangedBanner:
            self.showBanner(self.fileChangedWidget)

    def showFileDeletedBanner(self):
        """
        This function shows the file deleted banner
        """
        if self.env.settings.showFileChangedBanner:
            self.showBanner(self.fileDeletedWidget)

    def isFileChangedBannerVisible(self) -> bool:
        return self.fileChangedWidget.isVisible()

    def showSearchBar(self):
        if not self.searchBar:
            self.searchBar = SearchBar(self.env,self)
            self.mainLayout.addWidget(self.searchBar)

    def hideSearchBar(self):
        if self.searchBar:
            self.searchBar.close()
            self.mainLayout.removeWidget(self.searchBar)
            self.searchBar = None
