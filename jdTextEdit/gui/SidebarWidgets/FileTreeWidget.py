from jdTextEdit.api.SidebarWidgetBase import SidebarWidgetBase
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import QTreeView
from PyQt6.QtCore import QModelIndex
from typing import TYPE_CHECKING
import os


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class FileTreeWidget(QTreeView, SidebarWidgetBase):
    def __init__(self, env: "Environment") -> None:
        QTreeView.__init__(self)
        self.env = env

        model = QFileSystemModel()
        model.setRootPath('/')
        self.setModel(model)
        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(3)
        self.doubleClicked.connect(self.fileOpen)

    def fileOpen(self, signal: QModelIndex) -> None:
        path = self.model().filePath(signal)
        if os.path.isfile(path):
            self.env.pluginAPI.openFile(path)

    def getName(self) -> str:
        return QCoreApplication.translate("FileTreeWidget", "Files")

    def getID(self) -> str:
        return "files"
