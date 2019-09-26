from TranslationHelper import TranslationHelper
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QIcon
from Settings import Settings
from LexerList import getLexerList
from Functions import getTemplates, getDataPath
import json
import os

class SharedEnviroment():
    def __init__(self):
        self.version = "1.0"
        self.programDir = os.path.dirname(os.path.realpath(__file__))
        self.dataDir = getDataPath()#os.path.join(self.programDir,"data")

        if not os.path.isdir(self.dataDir):
            os.mkdir(self.dataDir)

        self.settings = Settings()
        if os.path.isfile(os.path.join(self.dataDir,"settings.json")):
            self.settings.load(os.path.join(self.dataDir,"settings.json"))
        
        if self.settings.language == "default":
            self.translations = TranslationHelper(QLocale.system().name().split("_")[0])
        else:
            self.translations = TranslationHelper(self.settings.language)

        self.recentFiles = []
        if os.path.isfile(os.path.join(self.dataDir,"recentfiles.json")):
            with open(os.path.join(self.dataDir,"recentfiles.json")) as f:
                self.recentFiles = json.load(f)

        #self.styles = {}
        #styleList = os.listdir(os.path.join(self.programDir,"styles"))
        #for i in styleList:
        #    with open(os.path.join(self.programDir,"styles",i)) as f:
        #        self.styles[i[:-5]] = json.load(f)
    
        self.lexerList = getLexerList()
        self.templates = []
        self.templates = getTemplates(os.path.join(self.programDir,"templates"),self.templates)
        self.templates = getTemplates(os.path.join(self.dataDir,"templates"),self.templates)
 
        self.commands = []
        if os.path.isfile(os.path.join(self.dataDir,"commands.json")):
            with open(os.path.join(self.dataDir,"commands.json")) as f:
                self.commands = json.load(f)
       
        self.dockWidgtes = []
        self.menuActions = {}
        self.plugins = {}

        self.documentSavedIcon = QIcon(os.path.join(self.programDir,"icons","document-saved.png"))
        self.documentUnsavedIcon = QIcon(os.path.join(self.programDir,"icons","document-unsaved.png"))

    def translate(self, string):
        #Just a litle shortcut
        return self.translations.translate(string)

    def saveRecentFiles(self):
        with open(os.path.join(self.dataDir,"recentfiles.json"), 'w', encoding='utf-8') as f:
            json.dump(self.recentFiles, f, ensure_ascii=False, indent=4)
