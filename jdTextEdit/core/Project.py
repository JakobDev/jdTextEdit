from PyQt6.QtCore import QObject, QFileSystemWatcher
import glob
import os


class Project(QObject):
    def __init__(self, env, project_id: str, name: str, path: str):
        super().__init__()
        self.env = env

        self._watcher = QFileSystemWatcher()
        self._project_id = project_id
        self._rootDir = path
        self._fileList = []
        self._dirList = []
        self._name = name

        self._updateList()
        #print(self._watcher.directories())
        self._watcher.directoryChanged.connect(self._directory_changed)

    def _updateList(self):
        newFileList = []
        newDirList = []
        for i in glob.glob(os.path.join(self._rootDir, "**/**"), recursive=True):
            localPath = self.getInternalPath(i)
            if os.path.isfile(i):
                if localPath not in newFileList:
                    newFileList.append(localPath)
            elif os.path.isdir(i):
                self._watcher.addPath(os.path.normpath(i))
                newDirList.append(localPath)
        self._fileList = newFileList
        self._dirList = newDirList

    def _directory_changed(self, path: str):
        self._updateList()
        internal_dir =  self.getInternalPath(path)
        """
        directory_list = self.getDirectoryFiles(internal_dir)
        real_files = os.listdir(path)
        for i in directory_list:
            if i not in real_files:
                realPath = os.path.join(path, i)
                if os.path.isfile(realPath):
                    self._fileList.remove(os.path.join(internal_dir, i))
                elif os.path.isdir(realPath):
                    self._addDirectory(realPath)
        for i in real_files:
            if not i in directory_list:
                self._fileList.append(os.path.join(internal_dir, i))
        """
        self.env.projectSignals.directoryChanged.emit(self, internal_dir)

    def getName(self) -> str:
        return self._name

    def getRootDir(self) -> str:
        return self._rootDir

    def getInternalPath(self, path: str) -> str:
        return path.replace(self._rootDir, "")[1:]

    def getAbsolutePath(self, path: str) -> str:
        return os.path.join(self._rootDir, path)

    def getFileList(self):
        return self._fileList

    def getDirectoryList(self):
        return self._dirList

    def getDirectoryFiles(self, path: str):
        dirFileList = []
        for i in self._fileList:
            if i.startswith(path):
                dirFileList.append(os.path.basename(i))
        return dirFileList

    def getID(self) -> str:
        return self._project_id
