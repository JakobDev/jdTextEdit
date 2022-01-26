from jdTextEdit.api.LanguageBase import LanguageBase
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.api.SidebarWidgetBase import SidebarWidgetBase
from jdTextEdit.core.api.EditorSignals import EditorSignals
from jdTextEdit.core.api.MainWindowSignals import MainWindowSignals
from jdTextEdit.core.api.ApplicationSignals import ApplicationSignals
from jdTextEdit.core.api.ProjectSignals import ProjectSignals
from jdTextEdit.api.ThemeBase import ThemeBase
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QAction


class PluginAPI():
    def __init__(self,env):
        self.env = env

    def addLanguage(self,language: LanguageBase):
        self.env.languageList.append(language)

    def getEditorSignals(self) -> EditorSignals:
        return self.env.editorSignals

    def getMainWindowSignals(self) -> MainWindowSignals:
        return self.env.mainWindowSignals

    def getApplicationSignals(self) -> ApplicationSignals:
        return self.env.applicationSignals

    def getProjectSignals(self) -> ProjectSignals:
        return self.env.projectSignals

    def addSettingsTab(self, tab: SettingsTabBase):
        self.env.customSettingsTabs.append(tab)

    def registerSetting(self,key: str,value: str):
        self.env.settings.register(key,value)
        self.env.defaultSettings.append([key,value])

    def addTranslationDirectory(self,path: str):
        self.env.translations.loadDirectory(path)

    def addBigFilesCheckBox(self,setting: str, text:str):
        self.env.customBigFilesSettings.append([setting,text])

    def addTheme(self, theme: ThemeBase):
        self.env.themes[theme.getID()] = theme

    def addSidebarWidget(self, widget: SidebarWidgetBase):
        if not isinstance(widget, QWidget) or not isinstance(widget, SidebarWidgetBase):
            raise ValueError("Widget must inherit from QWidget and SidebarWidgetBase")
        self.env.dockWidgets.append([widget, widget.getName(), widget.getID()])

    def addAction(self,action: QAction):
        try:
            if isinstance(action.data()[0], str):
                self.env.menuActions[action.data()[0]] = action
        except Exception:
            pass

    def addProject(self, project):
        self.env.projects[project.getID()] = project
        self.getProjectSignals().projectAdded.emit(project)

    def deleteProject(self, projectID: str):
        del self.env.projects[projectID]
        self.getProjectSignals().projectDeleted.emit(projectID)
