from jdTranslationHelper import jdTranslationHelper
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QIcon
from jdTextEdit.Settings import Settings
from jdTextEdit.LexerList import getLexerList
from jdTextEdit.Functions import getTemplates, getDataPath, showMessageBox
import charset_normalizer
import cchardet
import chardet
import argparse
import shutil
import json
import sys
import os

class Enviroment():
    def __init__(self):
        self.version = "6.0"
        self.programDir = os.path.dirname(os.path.realpath(__file__))

        parser = argparse.ArgumentParser()
        parser.add_argument("filename",nargs="*")
        parser.add_argument("-p", "--portable",action="store_true", dest="portable",help="Portable")
        self.args = parser.parse_args().__dict__
        if self.args["portable"]:
            self.dataDir = os.path.join(self.programDir,"data")
        else:
            self.dataDir = getDataPath()

        if not os.path.isdir(self.dataDir):
            try:
                if os.path.isdir(os.path.join(self.programDir,"default_data")):
                    shutil.copytree(os.path.join(self.programDir,"default_data"), self.dataDir)
                else:
                    os.mkdir(self.dataDir)
            except:
                showMessageBox("Unable to create data folder","jdTextEdit is unable to create his data folder. Maybe you've installed it in a system directory and try to run it in portable mode")
                sys.exit(2)

        self.settings = Settings()
        if os.path.isfile(os.path.join(self.dataDir,"settings.json")):
            self.settings.load(os.path.join(self.dataDir,"settings.json"))
        
        if self.settings.language == "default":
            self.translations = jdTranslationHelper(lang=QLocale.system().name())
        else:
            self.translations = jdTranslationHelper(lang=self.settings.language)
        self.translations.loadDirectory(os.path.join(self.programDir,"translation"))

        self.recentFiles = []
        if os.path.isfile(os.path.join(self.dataDir,"recentfiles.json")):
            try:
                with open(os.path.join(self.dataDir,"recentfiles.json"),"r",encoding="utf-8") as f:
                    self.recentFiles = json.load(f)
            except:
                print("Can't read recentfiles.json")

        self.windowState = {}
        if os.path.isfile(os.path.join(self.dataDir,"windowstate.json")):
            try:
                with open(os.path.join(self.dataDir,"windowstate.json"),"r",encoding="utf-8") as f:
                    self.windowState = json.load(f)
            except:
                print("Can't read windowstate.json")

        self.macroList = []
        if os.path.isfile(os.path.join(self.dataDir,"macros.json")):
            try:
                with open(os.path.join(self.dataDir,"macros.json"),"r",encoding="utf-8") as f:
                    self.macroList = json.load(f)
            except:
                print("Can't read macros.json")

        #self.themes = {}
        #self.loadThemeDirectory(os.path.join(self.programDir,"themes"))
        #user_themes = os.path.join(self.dataDir,"themes")
        #if os.path.isdir(user_themes):
        #    self.loadThemeDirectory(user_themes)
        #else:
        #    os.mkdir(user_themes)
        #self.themes["default"] = {"meta":{"name":self.translate("settingsWindow.style.theme.default"),"id":"default"},"colors":{}}

        self.lexerList = getLexerList()
        self.templates = []
        self.templates = getTemplates(os.path.join(self.programDir,"templates"),self.templates)
        self.templates = getTemplates(os.path.join(self.dataDir,"templates"),self.templates)

        self.commands = []
        if os.path.isfile(os.path.join(self.dataDir,"commands.json")):
            try:
                with open(os.path.join(self.dataDir,"commands.json"),"r",encoding="utf-8") as f:
                    self.commands = json.load(f)
            except:
                print("Can't read commands.json")

        self.dockWidgtes = []
        self.menuActions = {}
        self.encodingAction = []
        self.plugins = {}

        self.encodingDetectFunctions = {
            "chardet": chardet.detect,
            "charset_normalizer": charset_normalizer.detect,
            "cChardet": cchardet.detect
        }

        self.documentSavedIcon = QIcon(os.path.join(self.programDir,"icons","document-saved.png"))
        self.documentUnsavedIcon = QIcon(os.path.join(self.programDir,"icons","document-unsaved.png"))

        self.defaultStyle = QApplication.style().metaObject().className()[1:-5]

    def translate(self, string):
        #Just a litle shortcut
        return self.translations.translate(string)

    def loadThemeDirectory(self,path):
        themeList = os.listdir(path)
        for i in themeList:
            with open(os.path.join(path,i)) as f:
                singleTheme = json.load(f)
                self.themes[singleTheme["meta"]["id"]] = singleTheme

    def saveRecentFiles(self):
        with open(os.path.join(self.dataDir,"recentfiles.json"), 'w', encoding='utf-8') as f:
            json.dump(self.recentFiles, f, ensure_ascii=False, indent=4)
