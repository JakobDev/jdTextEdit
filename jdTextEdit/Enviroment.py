from jdTranslationHelper import jdTranslationHelper
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QLocale, QTranslator
from PyQt6.QtGui import QIcon
from jdTextEdit.Settings import Settings
from jdTextEdit.LexerList import getLexerList
from jdTextEdit.Functions import getTemplates, getDataPath, showMessageBox, readJsonFile, getFullPath, loadProjects, isFlatpak
from jdTextEdit.core.BuiltinLanguage import BuiltinLanguage
from jdTextEdit.core.api.EditorSignals import EditorSignals
from jdTextEdit.core.api.MainWindowSignals import MainWindowSignals
from jdTextEdit.core.api.ApplicationSignals import ApplicationSignals
from jdTextEdit.core.api.TabWidgetSignals import TabWidgetSignals
from jdTextEdit.core.api.ProjectSignals import ProjectSignals
from jdTextEdit.core.api.PluginAPI import PluginAPI
from jdTextEdit.core.DefaultTheme import DefaultTheme
from jdTextEdit.core.FileTheme import FileTheme
from jdTextEdit.api.LanguageBase import LanguageBase
from typing import List
import argparse
import chardet
import shutil
import json
import sys
import os

class Enviroment():
    def __init__(self, app: QApplication):
        self.programDir = os.path.dirname(os.path.realpath(__file__))

        with open(os.path.join(self.programDir, "version.txt"), "r", encoding="utf-8") as f:
            self.version = f.read().strip()

        parser = argparse.ArgumentParser()
        parser.add_argument("filename", nargs="*")
        parser.add_argument("-p", "--portable",action="store_true", dest="portable", help="Portable")
        parser.add_argument("--data-dir", dest="dataDir",help="Sets the data directory")
        parser.add_argument("--disable-plugins", action="store_true", dest="disablePlugins", help="Disable Plugins")
        parser.add_argument("--no-session-restore", action="store_true", dest="disableSessionRestore", help="Disable Session Restore")
        parser.add_argument("--disable-updater", action="store_true", dest="disableUpdater", help="Disable the Updater")
        parser.add_argument("--distribution-file", dest="distributionFile", help="Sets custom distribution.json")
        parser.add_argument("--language", dest="language", help="Starts jdTextEdit in the given language")
        parser.add_argument("--debug", action="store_true", dest="debug", help="Enable Debug mode")
        self.args = parser.parse_args().__dict__

        #if distributionFile:
        #    self.distributionSettings = readJsonFile(getFullPath(distributionFile),{})
        #else:
        self.distributionSettings = readJsonFile(self.args["distributionFile"] or os.path.join(self.programDir, "distribution.json"), {})

        if self.args["portable"]:
            self.dataDir = os.path.join(self.programDir, "data")
        else:
            self.dataDir = getDataPath(self)

        if not os.path.isdir(self.dataDir):
            self.firstRun = True
            try:
                if os.path.isdir(os.path.join(self.programDir, "default_data")):
                    shutil.copytree(os.path.join(self.programDir, "default_data"), self.dataDir)
                else:
                    os.makedirs(self.dataDir)
            except Exception:
                showMessageBox("Unable to create data folder", f"jdTextEdit is unable to create his data folder {self.dataDir}. Maybe you've installed it in a system directory and try to run it in portable mode")
                sys.exit(2)
        else:
            self.firstRun = False

        self.isFlatpak = isFlatpak()

        if not(self.distributionSettings.get("enableUpdater", True)) or self.args["disableUpdater"] or self.isFlatpak or os.getenv("JDTEXTEDIT_DISABLE_UPDATER"):
            self.enableUpdater = False
        else:
            self.enableUpdater = True

        self.settings = Settings()
        if os.path.isfile(os.path.join(self.dataDir, "settings.json")):
            self.settings.load(os.path.join(self.dataDir, "settings.json"))

        self._translator = QTranslator()
        if self.args["language"]:
            self.translations = jdTranslationHelper(self.args["language"])
            self._translator.load(os.path.join(self.programDir, "i18n", "jdTextEdit_" + self.args["language"] + ".qm"))
        elif self.settings.language == "default":
            self.translations = jdTranslationHelper(lang=QLocale.system().name())
            self._translator.load(os.path.join(self.programDir, "i18n", "jdTextEdit_" + QLocale.system().name() + ".qm"))
        else:
            self.translations = jdTranslationHelper(lang=self.settings.get("language"))
            self._translator.load(os.path.join(self.programDir, "i18n", "jdTextEdit_" + self.settings.get("language") + ".qm"))
        self.translations.loadDirectory(os.path.join(self.programDir, "translation"))
        app.installTranslator(self._translator)

        self.recentFiles = readJsonFile(os.path.join(self.dataDir, "recentfiles.json"),[])

        self.windowState = readJsonFile(os.path.join(self.dataDir, "windowstate.json"),{})

        self.macroList = readJsonFile(os.path.join(self.dataDir, "macros.json"),[])
        self.global_macroList = readJsonFile(os.path.join(self.programDir, "macros.json"),[])

        self.commands = readJsonFile(os.path.join(self.dataDir, "commands.json"),[])
        self.global_commands = readJsonFile(os.path.join(self.programDir, "commands.json"),[])

        self.themes = {}
        #self.loadThemeDirectory(os.path.join(self.programDir,"themes"))
        #user_themes = os.path.join(self.dataDir,"themes")
        #if os.path.isdir(user_themes):
        #    self.loadThemeDirectory(user_themes)
        #else:
        #    os.mkdir(user_themes)
        #self.themes["default"] = {"meta":{"name":self.translate("settingsWindow.style.theme.default"),"id":"default"},"colors":{}}

        self.menuList = []

        self.lexerList = getLexerList()

        self.languageList: List[LanguageBase] = []
        for i in self.lexerList:
            lang = BuiltinLanguage(self,i)
            self.languageList.append(lang)

        self.templates = []
        getTemplates(os.path.join(self.programDir,"templates"),self.templates)
        getTemplates(os.path.join(self.dataDir,"templates"),self.templates)
        if "templateDirectories" in self.distributionSettings:
            if isinstance(self.distributionSettings["templateDirectories"], list):
                for i in self.distributionSettings["templateDirectories"]:
                    getTemplates(getFullPath(i), self.templates)
            else:
                print("templateDirectories in distribution.json must be a list", file=sys.stderr)

        self.dockWidgets = []
        self.menuActions = {}
        self.encodingAction = []
        self.projects = loadProjects(self, os.path.join(self.dataDir, "projects.json"))
        self.plugins = {}

        self.encodingDetectFunctions = {
            "chardet": chardet.detect
        }

        try:
            import charset_normalizer
            self.encodingDetectFunctions["charset_normalizer"] =  charset_normalizer.detect
        except ImportError:
            pass

        try:
            import cchardet
            self.encodingDetectFunctions["cChardet"] = cchardet.detect
        except ImportError:
            pass

        self.lastSavePath = ""
        self.lastOpenPath = ""

        self.documentSavedIcon = QIcon(os.path.join(self.programDir, "icons", "document-saved.png"))
        self.documentUnsavedIcon = QIcon(os.path.join(self.programDir, "icons", "document-unsaved.png"))

        self.defaultStyle = QApplication.style().metaObject().className()[1:-5]

        self.editorSignals = EditorSignals()
        self.mainWindowSignals = MainWindowSignals()
        self.applicationSignals = ApplicationSignals()
        self.tabWidgetSignals = TabWidgetSignals()
        self.projectSignals = ProjectSignals()
        self.customSettingsTabs = []
        self.customBigFilesSettings = []
        self.defaultSettings = []
        self.pluginAPI = PluginAPI(self)

        self.pluginAPI.addTheme(DefaultTheme(self))

        self.loadThemeDirectory(os.path.join(self.programDir,"themes"))
        self.loadThemeDirectory(os.path.join(self.dataDir, "themes"))

    def translate(self, key: str) -> str:
        """
        Returns the Translation of the given key.
        :param key: The Key
        :return: The Translation
        """
        return self.translations.translate(key)

    def loadThemeDirectory(self,path):
        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except Exception:
                return
        themeList = os.listdir(path)
        for i in themeList:
            try:
                theme = FileTheme(os.path.join(path,i))
                self.pluginAPI.addTheme(theme)
            except Exception:
                pass

    def saveRecentFiles(self):
        with open(os.path.join(self.dataDir, "recentfiles.json"), 'w', encoding='utf-8') as f:
            json.dump(self.recentFiles, f, ensure_ascii=False, indent=4)
