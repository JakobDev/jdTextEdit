from jdTranslationHelper import jdTranslationHelper
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QLocale, QTranslator, QLibraryInfo, QCoreApplication, QMimeDatabase
from PyQt6.QtGui import QIcon
from jdTextEdit.Settings import Settings
from jdTextEdit.LexerList import getLexerList
from jdTextEdit.Functions import getTemplates, getDataPath, showMessageBox, readJsonFile, getFullPath, loadProjects, isFlatpak, getParentDirectory
from jdTextEdit.core.BuiltinLanguage import BuiltinLanguage
from jdTextEdit.core.api.EditorSignals import EditorSignals
from jdTextEdit.core.api.MainWindowSignals import MainWindowSignals
from jdTextEdit.core.api.ApplicationSignals import ApplicationSignals
from jdTextEdit.core.api.TabWidgetSignals import TabWidgetSignals
from jdTextEdit.core.api.ProjectSignals import ProjectSignals
from typing import Any, Optional, Callable, TYPE_CHECKING
from jdTextEdit.core.api.PluginAPI import PluginAPI
from jdTextEdit.core.DefaultTheme import DefaultTheme
from jdTextEdit.core.FileTheme import FileTheme
from jdTextEdit.api.LanguageBase import LanguageBase
from jdTextEdit.api.Types import LanguageOverwriteEntry
from jdTextEdit.core.Logger import getGlobalLogger
import importlib
import shutil
import json
import sys
import os


if TYPE_CHECKING:
    from jdTextEdit.api.ThemeBase import ThemeBase
    from .gui.MainWindow import MainWindow
    from jdTextEdit.api.Types import *
    from PyQt6.QtGui import QAction


class Environment():
    def __init__(self, app: QApplication, args: dict[str, Any]) -> None:
        self.programDir = os.path.dirname(os.path.realpath(__file__))
        self.app = app

        with open(os.path.join(self.programDir, "version.txt"), "r", encoding="utf-8") as f:
            self.version = f.read().strip()

        self.args = args

        self.logger = getGlobalLogger()

        self.distributionSettings: DistributionSettingsType = readJsonFile(self.args["distributionFile"] or os.path.join(self.programDir, "distribution.json"), {})

        if self.args["portable"]:
            self.dataDir = os.path.join(getParentDirectory(self.programDir), "jdTextEditData")
        else:
            self.dataDir = getDataPath(self)

        self.debugMode = bool(self.args["debug"])

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

        self._qtTranslator: list[QTranslator] = []
        self.loadQtTranslations(os.path.join(self.programDir, "translations"), "jdTextEdit_{{lang}}.qm")
        self.loadQtTranslations(QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath), "qt_{{lang}}.qm")
        self.loadQtTranslations(QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath), "qscintilla_{{lang}}.qm")
        if self.args["language"]:
            self.translations = jdTranslationHelper(lang=self.args["language"], default_language="en")
        elif self.settings.language == "default":
            system_lang = QLocale.system().name().split("_")[0]
            self.translations = jdTranslationHelper(lang=system_lang, default_language="en")
        else:
            self.translations = jdTranslationHelper(lang=self.settings.get("language"), default_language="en")

        self.recentFiles: list[str] = readJsonFile(os.path.join(self.dataDir, "recentfiles.json"), [])

        self.windowState: dict[str, dict[str, str]] = readJsonFile(os.path.join(self.dataDir, "windowstate.json"), {})

        self.macroList: list[dict[str, str]] = readJsonFile(os.path.join(self.dataDir, "macros.json"), [])
        self.global_macroList: list[dict[str, str]] = readJsonFile(os.path.join(self.programDir, "macros.json"), [])

        self.commands = readJsonFile(os.path.join(self.dataDir, "commands.json"), [])
        self.global_commands = readJsonFile(os.path.join(self.programDir, "commands.json"), [])

        self.themes: dict[str, "ThemeBase"] = {}
        #self.loadThemeDirectory(os.path.join(self.programDir,"themes"))
        #user_themes = os.path.join(self.dataDir,"themes")
        #if os.path.isdir(user_themes):
        #    self.loadThemeDirectory(user_themes)
        #else:
        #    os.mkdir(user_themes)
        #self.themes["default"] = {"meta":{"name":self.translate("settingsWindow.style.theme.default"),"id":"default"},"colors":{}}

        self.menuList = []

        self.lexerList = getLexerList()

        self.languageList: list[LanguageBase] = []
        for i in self.lexerList:
            lang = BuiltinLanguage(self, i)
            self.languageList.append(lang)

        self.languageOverwrites: dict[str, LanguageOverwriteEntry] = readJsonFile(os.path.join(self.dataDir, "languageOverwrites.json"), {"overwrites": {}})["overwrites"]
        self.updateTemplates()

        self.statusBarWidgetDict = {}

        self.dockWidgets = []
        self.menuActions: dict[str, "QAction"] = {}
        self.encodingAction: list["QAction"] = []
        self.projects = loadProjects(self, os.path.join(self.dataDir, "projects.json"))
        self.plugins: dict[str, dict[str, str]] = {}

        self.encodingDetectFunctions: dict[str, Callable[[bytes], EncodingDetectFunctionResult]] = {}
        for i in ("chardet", "charset_normalizer", "cchardet"):
            try:
                module = importlib.import_module(i)
                self.encodingDetectFunctions[i] = module.detect
            except ModuleNotFoundError:
                pass

        if len(self.encodingDetectFunctions) == 0:
            self.logger.warning("No libs for encoding detection found")

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
        self.customBigFilesSettings: list[list[str]] = []
        self.defaultSettings: list[tuple[str, str]] = []
        self.pluginAPI = PluginAPI(self)

        self.pluginAPI.addTheme(DefaultTheme(self))

        self.loadThemeDirectory(os.path.join(self.programDir, "themes"))
        self.loadThemeDirectory(os.path.join(self.dataDir, "themes"))

        self.exportDataList: list["ExportDataType"] = [
            {"id": "settings", "name": QCoreApplication.translate("Environment", "Settings"), "path": ["settings.json"]},
            {"id": "templates", "name": QCoreApplication.translate("Environment", "Templates"), "path": ["templates"]}
        ]

        self.mimeDatabase = QMimeDatabase()

        self.mainWindow: Optional["MainWindow"] = None

    def translate(self, key: str) -> str:
        """
        Returns the Translation of the given key.
        :param key: The Key
        :return: The Translation
        """
        return self.translations.translate(key)

    def loadQtTranslations(self, directory: str, filename: str) -> None:
        translator = QTranslator()

        if self.args["language"]:
            translator.load(os.path.join(directory, filename.replace("{{lang}}", self.args["language"])))
        elif self.settings.get("language") == "default":
            systemLang = QLocale.system().name()
            translator.load(os.path.join(directory, filename.replace("{{lang}}", systemLang.split("_")[0])))
            translator.load(os.path.join(directory, filename.replace("{{lang}}", systemLang)))
        else:
            translator.load(os.path.join(directory, filename.replace("{{lang}}", self.settings.get("language"))))

        self.app.installTranslator(translator)
        self._qtTranslator.append(translator)

    def loadThemeDirectory(self, path: str) -> None:
        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except Exception:
                return
        themeList = os.listdir(path)
        for i in themeList:
            try:
                theme = FileTheme(os.path.join(path, i))
                self.pluginAPI.addTheme(theme)
            except Exception:
                pass

    def saveRecentFiles(self) -> None:
        with open(os.path.join(self.dataDir, "recentfiles.json"), 'w', encoding='utf-8') as f:
            json.dump(self.recentFiles, f, ensure_ascii=False, indent=4)

    def updateTemplates(self) -> None:
        self.templates: list[list[str]] = []
        getTemplates(os.path.join(self.programDir, "templates"), self.templates)
        getTemplates(os.path.join(self.dataDir, "templates"), self.templates)
        if "templateDirectories" in self.distributionSettings:
            if isinstance(self.distributionSettings["templateDirectories"], list):
                for i in self.distributionSettings["templateDirectories"]:
                    getTemplates(getFullPath(i), self.templates)
            else:
                self.logger.error("templateDirectories in distribution.json must be a list")

    def getLanguageByID(self, languageID: str) -> Optional[LanguageBase]:
        for i in self.languageList:
            if i.getID() == languageID:
                return i
        return None
