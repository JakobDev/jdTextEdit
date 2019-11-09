from jdTextEdit.TranslationHelper import TranslationHelper
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QIcon
from jdTextEdit.Settings import Settings
from jdTextEdit.LexerList import getLexerList
from jdTextEdit.Functions import getTemplates, getDataPath, showMessageBox
from optparse import OptionParser
import json
import sys
import os

class Enviroment():
    def __init__(self):
        self.version = "5.1"
        self.programDir = os.path.dirname(os.path.realpath(__file__))

        parser = OptionParser()
        parser.add_option("-p", "--portable",action="store_true", dest="portable", default=False,help="Portable")
        self.options, self.args = parser.parse_args()
        if self.options.portable:
            self.dataDir = os.path.join(self.programDir,"data")
        else:
            self.dataDir = getDataPath()

        if not os.path.isdir(self.dataDir):
            try:
                os.mkdir(self.dataDir)
            except:
                showMessageBox("Unable to create data folder","jdTextEdit is unable to create his data folder. Maybe you've installed it in a system directory and try to run it in portable mode")
                sys.exit(2)

        self.settings = Settings()
        if os.path.isfile(os.path.join(self.dataDir,"settings.json")):
            self.settings.load(os.path.join(self.dataDir,"settings.json"))
        
        if self.settings.language == "default":
            self.translations = TranslationHelper(QLocale.system().name())
        else:
            self.translations = TranslationHelper(self.settings.language)

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
            try:
                with open(os.path.join(self.dataDir,"commands.json"),"r",encoding="utf-8") as f:
                    self.commands = json.load(f)
            except:
                print("Can't read commands.json")
       
        self.dockWidgtes = []
        self.menuActions = {}
        self.encodingAction = []
        self.plugins = {}

        self.documentSavedIcon = QIcon(os.path.join(self.programDir,"icons","document-saved.png"))
        self.documentUnsavedIcon = QIcon(os.path.join(self.programDir,"icons","document-unsaved.png"))

        self.defaultStyle = QApplication.style().metaObject().className()[1:-5]

    def translate(self, string):
        #Just a litle shortcut
        return self.translations.translate(string)

    def saveRecentFiles(self):
        with open(os.path.join(self.dataDir,"recentfiles.json"), 'w', encoding='utf-8') as f:
            json.dump(self.recentFiles, f, ensure_ascii=False, indent=4)
