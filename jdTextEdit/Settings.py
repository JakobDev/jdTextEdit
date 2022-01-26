from PyQt6.QtGui import QFont, QKeySequence
from jdTextEdit.Functions import showMessageBox, readJsonFile, isFlatpak
from pathlib import Path
from typing import Any
import platform
import json
import os

class Settings():
    def __init__(self, defaultSettings=None):
        self.language = "default"
        self.applicationStyle = "default"
        self.saveClose = True
        self.hideTabBar = False
        self.tabBarPosition = 0
        self.closeButtonTab = True
        self.allowTabMove = True
        self.tabDoubleClickClose = False
        self.maxRecentFiles = 10
        self.saveSession = True
        self.loadPlugins = True
        self.searchUpdates = False
        self.windowFileTitle = True
        self.saveWindowState = True
        self.eolFileEnd = False
        self.stripSpacesSave = False
        self.exitLastTab = True
        self.useIPC = True
        self.showToolbar = True
        self.toolbarPosition = 0
        self.toolbarIconStyle = 4
        self.useEditorConfig = True
        self.defaultEncoding = "UTF-8"
        self.defaultLanguage = -1
        self.editTheme = "builtin.default"
        self.useCustomFont = False
        self.startupDayTip = True
        self.editFont = QFont()
        self.editTabWidth = 4
        self.editTabSpaces = False
        self.editTextWrap = False
        self.editShowWhitespaces = False
        self.editAutoIndent = False
        self.editShowLineNumbers = True
        self.editShowEol = False
        self.showIndentationGuides = False
        self.detectEncoding = True
        self.detectEol = True
        self.detectLanguage = True
        self.encodingDetectLib = "chardet"
        self.saveBackupEnabled = False
        self.saveBackupExtension = ".bak"
        self.highlightCurrentLine = True
        self.editFoldStyle = 0
        self.defaultZoom = 0
        self.enableAutocompletion = True
        self.autocompletionUseDocument = True
        self.autocompletionUseAPI = True
        self.autocompletionCaseSensitive = True
        self.autocompletionReplaceWord = False
        self.autocompleteThreshold = 3
        self.editContextMenu = ["undo","redo","separator","cut","copy","paste","delete","separator","selectAll"]
        self.toolBar = ["newFile","openFile","saveFile","separator","cut","copy","paste","delete","separator","undo","redo"]
        self.showSidepane = False
        self.sidepaneWidget = "files"
        self.showFileChangedBanner = True
        self.showEncodingBanner = True
        self.showEolBanner = True
        self.enableAutoSave = False
        self.autoSaveInterval = 30
        self.enableBigFileLimit = True
        self.bigFileSize = 10485760
        self.bigFileDisableHighlight = True
        self.bigFileDisableEncodingDetect = True
        self.bigFileShowBanner = True
        self.saveFilePathType = 0
        self.saveFileCustomPath = str(Path.home())
        self.openFilePathType = 0
        self.openFileCustomPath = str(Path.home())
        self.editorConfigUseIndentStyle = True
        self.editorConfigTabWidth = True
        self.editorConfigEndOfLine = True
        self.editorConfigTrimWhitespace = True
        self.editorConfigInsertNewline = True
        self.editorConfigShowBanner = False
        self.settingsWindowUseModernDesign = True
        self.enableUserChrome = True
        self.swapOkCancel = True
        self.disabledPlugins = []
        self.shortcut = {
            "newFile": QKeySequence(QKeySequence.StandardKey.New).toString(),
            "openFile": QKeySequence(QKeySequence.StandardKey.Open).toString(),
            "saveFile": QKeySequence(QKeySequence.StandardKey.Save).toString(),
            "saveAsFile": QKeySequence(QKeySequence.StandardKey.SaveAs).toString(),
            "saveAll": "Shift+Alt+S",
            "closeTab": QKeySequence(QKeySequence.StandardKey.Close).toString(),
            "print": QKeySequence(QKeySequence.StandardKey.Print).toString(),
            "exit": QKeySequence(QKeySequence.StandardKey.Quit).toString(),
            "undo": QKeySequence(QKeySequence.StandardKey.Undo).toString(),
            "redo": QKeySequence(QKeySequence.StandardKey.Redo).toString(),
            "cut": QKeySequence(QKeySequence.StandardKey.Cut).toString(),
            "copy": QKeySequence(QKeySequence.StandardKey.Copy).toString(),
            "paste": QKeySequence(QKeySequence.StandardKey.Paste).toString(),
            "delete": QKeySequence(QKeySequence.StandardKey.Delete).toString(),
            "selectAll": QKeySequence(QKeySequence.StandardKey.SelectAll).toString(),
            "settings": QKeySequence(QKeySequence.StandardKey.Preferences).toString(),
            "zoomIn": QKeySequence(QKeySequence.StandardKey.ZoomIn).toString(),
            "zoomOut": QKeySequence(QKeySequence.StandardKey.ZoomOut).toString(),
            "fullscreen": QKeySequence(QKeySequence.StandardKey.FullScreen).toString(),
            "find": QKeySequence(QKeySequence.StandardKey.Find).toString(),
            "findReplaceWindow": QKeySequence(QKeySequence.StandardKey.Replace).toString(),
            "gotoLine": "Ctrl+L",
            "addRemoveBookmark": "Ctrl+F2",
            "nextBookmark": "F2",
            "previousBookmark": "Shift+F2",
            "playMacro": "Ctrl+Shift+P",
            "about": QKeySequence(QKeySequence.StandardKey.HelpContents).toString(),
        }
        self.useCustomTerminalEmulator = False
        self.customTerminalEmulator = ""
        if platform.system() == 'Windows':
            self.defaultEolMode = 0
        else:
            self.defaultEolMode = 1
        if os.getenv("SNAP") or isFlatpak():
            self.useNativeIcons = False
        else:
            self.useNativeIcons = True
        if defaultSettings:
            for i in defaultSettings:
                setattr(self,i[0],i[1])

    def loadDict(self, data: dict):
        """
        Loads Settings from a dict
        :param data: The dict
        """
        settings = vars(self)
        for key, value in data.items():
            settings[key] = value
        if "editFont" in data:
            font = QFont()
            font.fromString(settings["editFont"])
            settings["editFont"] = font

    def load(self, path: str):
        """
        Loads settings from a file
        :param path: The path of the file
        """
        data = readJsonFile(path,None)
        if data:
            self.loadDict(data)
        else:
            showMessageBox("Can't load settings","The settings can't be loaded. jdTextEdit will use the default settings.")

    def save(self, path: str):
        """
        Save all Settings to a file
        :param path: The path of the file
        """
        data = vars(self)
        font = self.editFont
        data["editFont"] = self.editFont.toString()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        self.editFont = font

    def get(self, key: str) -> Any:
        """
        Returns the Value of a Setting
        :param key: The Key
        :return: The Value
        """
        return vars(self)[key]

    def set(self,key: str, value: Any):
        """
        Sets a setting
        :param key: The Key
        :param value: The new Value
        :return:
        """
        vars(self)[key] = value

    def register(self,key: str,value: Any):
        """
        Register a new setting
        :param key: The Key
        :param value: The default Value
        """
        if not hasattr(self,key):
            setattr(self,key,value)
