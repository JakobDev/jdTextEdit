from jdTextEdit.api.LanguageBase import LanguageBase
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.api.SidebarWidgetBase import SidebarWidgetBase
from jdTextEdit.core.api.EditorSignals import EditorSignals
from jdTextEdit.core.api.MainWindowSignals import MainWindowSignals
from jdTextEdit.core.api.ApplicationSignals import ApplicationSignals
from jdTextEdit.core.api.ProjectSignals import ProjectSignals
from jdTextEdit.api.ThemeBase import ThemeBase
from PyQt6.QtWidgets import QWidget, QMenu
from typing import TYPE_CHECKING
from PyQt6.QtGui import QAction


if TYPE_CHECKING:
    from jdTextEdit.gui.MainWindow import MainWindow
    from jdTextEdit.Environment import Environment


class PluginAPI():
    def __init__(self, env: "Environment"):
        self._env = env

    def addLanguage(self, language: LanguageBase):
        self._env.languageList.append(language)

    def getEditorSignals(self) -> EditorSignals:
        return self._env.editorSignals

    def getMainWindowSignals(self) -> MainWindowSignals:
        return self._env.mainWindowSignals

    def getApplicationSignals(self) -> ApplicationSignals:
        return self._env.applicationSignals

    def getProjectSignals(self) -> ProjectSignals:
        return self._env.projectSignals

    def addSettingsTab(self, tab: SettingsTabBase):
        self._env.customSettingsTabs.append(tab)

    def registerSetting(self, key: str, value: str):
        self._env.settings.register(key, value)
        self._env.defaultSettings.append((key, value))

    def addTranslationDirectory(self, path: str):
        self._env.translations.loadDirectory(path)

    def addBigFilesCheckBox(self, setting: str, text: str):
        self._env.customBigFilesSettings.append([setting, text])

    def addTheme(self, theme: ThemeBase):
        self._env.themes[theme.getID()] = theme

    def addSidebarWidget(self, widget: SidebarWidgetBase):
        if not isinstance(widget, QWidget) or not isinstance(widget, SidebarWidgetBase):
            raise ValueError("Widget must inherit from QWidget and SidebarWidgetBase")
        self._env.dockWidgets.append([widget, widget.getName(), widget.getID()])

    def addAction(self, action: QAction):
        try:
            if isinstance(action.data()[0], str):
                self._env.menuActions[action.data()[0]] = action
        except Exception:
            pass

    def addProject(self, project):
        self._env.projects[project.getID()] = project
        self.getProjectSignals().projectAdded.emit(project)

    def deleteProject(self, projectID: str):
        del self._env.projects[projectID]
        self.getProjectSignals().projectDeleted.emit(projectID)

    def addStatusBarWidget(self, widget):
        self._env.statusBarWidgetDict[widget.getID()] = widget

    def openFile(self, path: str) -> None:
        """Opens the File"""
        self._env.mainWindow.openFile(path)

    def getMainWindowList(self) -> list["MainWindow"]:
        return [self._env.mainWindow]

    def addMainWindowMenu(self, name: str) -> QMenu:
        return self._env.mainWindow.menuBar().addMenu(name)
