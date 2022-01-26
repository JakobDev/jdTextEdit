from jdTextEdit.api.SidebarWidgetBase import SidebarWidgetBase
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PyQt6.QtGui import QAction, QCursor, QContextMenuEvent
from jdTextEdit.core.Project import Project
from PyQt6.QtCore import QCoreApplication
from PyQt6 import sip
import os


class ProjectItem(QTreeWidgetItem):
    def setProject(self, project: Project):
        self._project = project

    def project(self):
        return self._project


class FileItem(QTreeWidgetItem):
    def setPath(self, path: str):
        self._path = path

    def setProject(self, project):
        self._project = project

    def path(self) -> str:
        return self._path

    def project(self):
        return self._project


class ProjectWidget(QTreeWidget, SidebarWidgetBase):
    def __init__(self, env):
        super().__init__()
        self.env = env

        self.rootItems = {}
        self.projectDict = {}
        self.itemDict = {}

        self.setHeaderLabels([QCoreApplication.translate("ProjectWidget", "Projects")])

        env.pluginAPI.getProjectSignals().directoryChanged.connect(self._projectDirectoryChanged)
        env.pluginAPI.getProjectSignals().projectAdded.connect(self._addProject)
        env.pluginAPI.getProjectSignals().projectDeleted.connect(self._projectDeleted)

        for key, value in env.projects.items():
            self._addProject(value)

        self.itemDoubleClicked.connect(self._itemClickedTriggered)

    def _addItems(self, project, root_item):
        projectID = project.getID()
        if projectID not in self.itemDict:
            self.itemDict[projectID] = {}
        item_dict = self.itemDict[projectID]
        fileList = project.getFileList()
        for i in fileList:
            parts = i.split(os.sep)
            current_item = root_item
            current_dict = item_dict
            for part in parts:
                if part not in current_dict:
                    new_item = FileItem(current_item)
                    new_item.setText(0, part)
                    new_item.setPath(i)
                    new_item.setProject(project)
                    current_item = new_item
                    new_dict = {}
                    new_dict["item"] = new_item
                    new_dict["dict"] = {}
                    current_dict[part] = new_dict
                    current_dict = new_dict
                    self.projectDict[projectID][i] = new_item
                else:
                    current_item = current_dict[part]["item"]
                    current_dict = current_dict[part]["dict"]
        for key, value in self.projectDict[projectID].items():
            if key not in fileList:
                parent = value.parent()
                parent.removeChild(value)

    def _addProject(self, project):
        projectID = project.getID()
        projectName = project.getName()
        self.projectDict[projectID] = {}
        root_item = ProjectItem(0)
        root_item.setProject(project)
        root_item.setText(0, projectName)
        self._addItems(project, root_item)
        self.rootItems[projectID] = root_item

        self.addTopLevelItem(root_item)

    def _projectDirectoryChanged(self, project, path):
        projectName = project.getName()
        self._addItems(project, self.rootItems[projectName])

    def _itemClickedTriggered(self, item):
        if not type(item) is FileItem:
            return
        path = item.project().getAbsolutePath(item.path())
        self.env.mainWindow.openFile(path)

    def _projectDeleted(self, projectID: str):
        sip.delete(self.rootItems[projectID])

    def _removeProject(self):
        action = self.sender()
        if action:
            self.env.pluginAPI.deleteProject(action.data())

    def contextMenuEvent(self, event: QContextMenuEvent):
        item = self.itemAt(event.pos())

        menu = QMenu("Menu", self)

        newProjectAction = QAction(QCoreApplication.translate("ProjectWidget", "New Project"), self)
        newProjectAction.triggered.connect(lambda: self.env.addProjectWindow.show())
        menu.addAction(newProjectAction)

        if item:
            if type(item) is ProjectItem:
                removeProjectAction = QAction(QCoreApplication.translate("ProjectWidget", "Remove Project"), self)
                removeProjectAction.triggered.connect(self._removeProject)
                removeProjectAction.setData(item.project().getID())
                menu.addAction(removeProjectAction)

        menu.popup(QCursor.pos())

    def getName(self) -> str:
        return QCoreApplication.translate("ProjectWidget", "Projects")

    def getID(self) -> str:
        return "builtin.project"
