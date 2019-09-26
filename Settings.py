from PyQt5.QtGui import QFont
import json

class Settings():
    def __init__(self):
        self.language = "default"
        self.saveClose = True
        self.hideTabBar = False
        self.maxRecentFiles = 10
        self.saveSession = True
        self.loadPlugins = True
        self.useNativeIcons = True
        self.showToolbar = True
        self.editStyle = "Default"
        self.useCustomFont = False
        self.startupDayTip = True
        self.editFont = QFont()
        self.editTabWidth = 8
        self.editTabSpaces = False
        self.editTextWrap = False
        self.editShowWhitespaces = False
        self.editAutoIndent = False
        self.editShowLineNumbers = True
        self.editShowEol = False
        self.highlightCurrentLine = True
        self.editFoldStyle = 0
        self.enableAutocompletion = True
        self.autocompletionUseDocument = True
        self.autocompletionUseAPI = True
        self.autocompletionCaseSensitive = True
        self.autocompletionReplaceWord = False
        self.autocompleteThreshold = 3
        self.editContextMenu = ["undo","redo","separator","cut","copy","paste","delete","separator","selectAll"]
        self.toolBar = ["newFile","fileOpen","saveFile","separator","cut","copy","paste","delete","separator","undo","redo"]
        self.showSidepane = False
        self.sidepaneWidget = "notes"
        #self.disabledPlugins = {}

    def load(self, path):
        settings = vars(self)
        with open(path) as f:
            data = json.load(f)
        for key, value in data.items():
            settings[key] = value
        if "editFont" in data:
            font = QFont()
            font.fromString(settings["editFont"])
            settings["editFont"] = font
        
    def save(self, path):
        data = vars(self)
        font = self.editFont
        data["editFont"] = self.editFont.toString()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        self.editFont = font
