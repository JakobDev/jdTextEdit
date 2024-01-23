from PyQt6.QtWidgets import QMessageBox, QWidget, QComboBox, QStatusBar
from typing import Any, Optional, Union, TYPE_CHECKING
from jdTextEdit.core.Logger import getGlobalLogger
from PyQt6.QtCore import Qt, QCoreApplication
from jdTextEdit.core.Project import Project
from jdTextEdit.Constants import Constants
from PyQt6.QtGui import QIcon, QAction
import subprocess
import platform
import tempfile
import datetime
import pathlib
import logging
import getpass
import shutil
import json
import sys
import re
import os


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment
    from jdTextEdit.gui.CodeEdit import CodeEdit
    from jdTextEdit.Settings import Settings
    from PyQt6.Qsci import QsciLexer


def getTemplates(path: str, templatelist: list[list[str]]):
    """
    Parses a template directory and stores it's content in a list
    :param path: directory
    :param templatelist: list
    """
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except Exception:
            getGlobalLogger().critical(f"Could not create template directory {path}")
            return
    filelist = os.listdir(path)
    for i in filelist:
        templatePath = os.path.join(path, i)
        if os.path.isfile(templatePath):
            templatelist.append([i, templatePath])


def _getSystemTerminalEmulator() -> Optional[str]:
    """
    Tries to find a working Terminal Emulator
    :return:
    """
    for i in ("x-terminal-emulator", "konsole", "gnome-terminal", "xterm"):
        if shutil.which(i) is not None:
            return i
        elif os.path.isfile(os.path.join("/run/host/usr/bin", i)):
            return i
    return None


def executeCommand(env: "Environment", command: str, editWidget: "CodeEdit", terminal: bool):
    """
    Executes a command. This function is used by the execute menu.
    :param env: the Environment
    :param command: the command
    :param editWidget: the edit widget
    :param terminal: I(f set to True, the command will be executed in a terminal emulator
    """
    command = command.replace("%url%", "file://" + editWidget.getFilePath())
    command = command.replace("%path%", editWidget.getFilePath())
    command = command.replace("%directory%", os.path.dirname(editWidget.getFilePath()))
    command = command.replace("%filename%", os.path.basename(editWidget.getFilePath()))
    command = command.replace("%selection%", editWidget.selectedText())
    if terminal:
        if platform.system() == 'Windows':
            subprocess.Popen(["cmd.exe", "/C", command])
        elif platform.system() == 'Darwin':
            #subprocess.call(('open', filepath))
            pass
        elif platform.system() == "Haiku":
            subprocess.Popen(["/system/apps/Terminal", command])
        elif os.getenv("SNAP"):
            subprocess.Popen([os.path.join(os.getenv("SNAP"), "usr", "bin", "xterm"), "-e", command])
        else:
            if env.settings.get("useCustomTerminalEmulator"):
                try:
                    if isFlatpak():
                        subprocess.Popen(["flatpak-spawn", "--host", env.settings.get("customTerminalEmulator"), "-e", command])
                    else:
                        subprocess.Popen([env.settings.get("customTerminalEmulator"), "-e", command])
                except FileNotFoundError:
                    QMessageBox.critical(None, QCoreApplication.translate("Functions", "Terminal emulator not found"),
                                         QCoreApplication.translate("Functions", "Your custom terminal emulator was not found"))
            else:
                systemEmulator = _getSystemTerminalEmulator()
                if systemEmulator is None:
                    QMessageBox.critical(None, QCoreApplication.translate("Functions", "Terminal emulator not found"),
                                         QCoreApplication.translate("Functions", "The terminal emulator of the system was not found. Try setting a custom one in the Settings."))
                else:
                    if isFlatpak():
                        subprocess.Popen(["flatpak-spawn", "--host", systemEmulator, "-e", command])
                    else:
                        subprocess.Popen([systemEmulator, "-e", command])
    else:
        if isFlatpak():
            os.popen("flatpak-spawn --host " + command)
        else:
            os.popen(command)


def getThemeIcon(env: "Environment", name: str) -> QIcon:
    """
    Returns the Icon from Theme. If the Theme doesn't contain the given Icon, it returns the Icon from jdTextEdit.
    :param env: Enviroment
    :param name: The name of Icon
    :return: The Icon
    """
    if QIcon.themeName() and env.settings.useNativeIcons:
        return QIcon.fromTheme(name)
    else:
        return QIcon(os.path.join(env.programDir, "icons/" + name + ".png"))


def openFileDefault(filepath: str):
    """
    Open a file or directory with the default program of the system.
    :param filepath: path
    """
    if platform.system() == 'Windows':
        os.startfile(filepath)
    elif platform.system() == 'Darwin':
        subprocess.call(('open', filepath))
    elif platform.system() == "Haiku":
        subprocess.call(('open', filepath))
    else:
        subprocess.call(('xdg-open', filepath))


def showMessageBox(title: str, text: str):
    """
    Shows a message box.
    :param title: the title
    :param text: the text
    """
    messageBox = QMessageBox()
    messageBox.setWindowTitle(title)
    messageBox.setText(text)
    messageBox.setStandardButtons(QMessageBox.StandardButton.Ok)
    messageBox.exec()


def getDataPath(env: "Environment") -> str:
    """
    Returns the Path to the data directory of jdTextEdit
    :param env: Environment
    :return: The Path
    """
    if env.args["dataDir"]:
        return getFullPath(env.args["dataDir"])
    elif os.getenv("JDTEXTEDIT_DATA_PATH"):
        return getFullPath(os.getenv("JDTEXTEDIT_DATA_PATH"))
    elif "dataDirectory" in env.distributionSettings:
        return getFullPath(env.distributionSettings["dataDirectory"])
    elif os.getenv("SNAP_USER_DATA"):
        return os.path.join(os.getenv("SNAP_USER_DATA"), "jdTextEdit")
    elif platform.system() == "Windows":
        return os.path.join(os.getenv("appdata"), "jdTextEdit")
    elif platform.system() == "Darwin":
        return os.path.join(str(pathlib.Path.home()), "Library", "Application Support", "jdTextEdit")
    elif platform.system() == "Haiku":
        return os.path.join(str(pathlib.Path.home()), "config", "settings", "jdTextEdit")
    else:
        if os.getenv("XDG_DATA_HOME"):
            return os.path.join(os.getenv("XDG_DATA_HOME"), "jdTextEdit")
        else:
            return os.path.join(str(pathlib.Path.home()), ".local", "share", "jdTextEdit")


def saveWindowState(window: QWidget, windict: dict[str, dict[str, Any]], winid: str):
    """
    Saves the state of the Window in the given dict
    :param window: The Window
    :param windict: The Dict
    :param winid: The ID of the Window
    """
    windict[winid] = {}
    x, y, w, h = window.geometry().getRect()
    windict[winid]["x"] = x
    windict[winid]["y"] = y
    windict[winid]["width"] = w
    windict[winid]["height"] = h
    windict[winid]["maximized"] = window.isMaximized()


def restoreWindowState(window: QWidget, windict: dict, winid: str):
    """
    Retores a Window from the given dict
    :param window: The Window
    :param windict: The Dict
    :param winid: The ID of the Window
    """
    if winid in windict:
        window.setGeometry(windict[winid]["x"], windict[winid]["y"], windict[winid]["width"], windict[winid]["height"])
        if windict.get("maximized", False):
            window.setWindowState(Qt.WindowStates.WindowMaximized)


def getTempOpenFilePath() -> str:
    """
    Returns the path of the temporary file that is used for IPC
    :return: path
    """
    return os.path.join(tempfile.gettempdir(), "jdTextEdit_" + getpass.getuser() + ".tmp")


def selectComboBoxItem(comboBox: QComboBox, item: str) -> None:
    """
    Selects the given item in a QComboBox
    :param comboBox: The QComboBox
    :param item: The  Item
    """
    for i in range(comboBox.count()):
        if comboBox.itemText(i) == item:
            comboBox.setCurrentIndex(i)


def readJsonFile(path: str, default: Any) -> Any:
    """
    Tries to parse the given JSON file and prints a error if the file couldn't be parsed
    Returns default if the file is not found or couldn't be parsed
    :param path: the JSON file
    :param default: what should be returned in case parsing failed
    :return: content of file
    """
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except json.decoder.JSONDecodeError as e:
            getGlobalLogger().critical(f"Can't parse {os.path.basename(path)}: {e.msg}: line {e.lineno} column {e.colno} (char {e.pos})")
            return default
        except Exception:
            getGlobalLogger().critical("Can't read " + os.path.basename(path))
            return default
    else:
        return default


def getFullPath(path: str) -> str:
    """
    Replaces variables and placeholders in path with their values
    :param path: original path
    :return: new path
    """
    return os.path.expanduser(os.path.expandvars(path))


def isFilenameValid(filename: str) -> bool:
    """
    Checks if a filename contains chars that are used to separate folder e.g. /
    This function does not check for illegal chars
    :param filename: the filename
    :return: valid
    """
    if filename.find("/") == -1 and filename.find("\\") == -1:
        return True
    else:
        return False


def saveProjects(projectDict: dict[str, Project], path: str) -> None:
    """
    Saves to projects to a file
    :param projectDict:
    :param path:
    :return:
    """
    if len(projectDict) == 0:
        if os.path.isfile(path):
            os.remove(path)
        return
    saveDict = {}
    for key, value in projectDict.items():
        saveDict[key] = {}
        saveDict[key]["name"] = value.getName()
        saveDict[key]["path"] = value.getRootDir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(saveDict, f, ensure_ascii=False, indent=4)


def loadProjects(env: "Environment", path: str) -> dict[str, Project]:
    """
    Loads the projects from a file
    :param env:
    :param path:
    :return:
    """
    data: dict[str, dict[str, str]] = readJsonFile(path, {})
    projectDict = {}
    for key, value in data.items():
        projectDict[key] = Project(env, key, value["name"], value["path"])
    return projectDict


def isFlatpak() -> bool:
    """
    Checks if jdTextEdit runs as Flatpak
    :return: isFlatpak
    """
    return os.path.isdir("/app")


def clearStatusBar(bar: QStatusBar):
    """
    Removes all Widgets from a QStatusBar
    :param bar: The Statusbar
    :return:
    """
    for i in bar.children():
        if isinstance(i, QWidget):
            bar.removeWidget(i)


def getRegExErrorMessage(regEx: str) -> Optional[str]:
    """
    Gets the error message for a RegEx
    :param regEx: The RegEx
    :return: The error or None if valid
    """
    try:
        re.compile(regEx)
        return None
    except re.error as ex:
        return QCoreApplication.translate("Functions", "Line {{line}} Column {{column}}: {{message}}").replace("{{line}}", str(ex.lineno)).replace("{{column}}", str(ex.colno)).replace("{{message}}", ex.msg)


def formatGermanUmlaute(text: str) -> str:
    """
    Use this function for the key argument of sorted to support German Umlaute
    """
    text = text.lower()
    text = text.replace("ä", "ae")
    text = text.replace("ü", "ue")
    text = text.replace("ö", "oe")
    text = text.replace("ß", "ss")
    return text


def sortActionDict(actionDict: dict[str, QAction]) -> dict[str, QAction]:
    tempDict = {}
    for key, value in actionDict.items():
        tempDict[value.text().removeprefix("&")] = key
    sortedDict = {}
    for i in sorted(tempDict.keys(), key=formatGermanUmlaute):
        sortedDict[tempDict[i]] = actionDict[tempDict[i]]
    return sortedDict


def formatDateTime(settings: "Settings", dt: datetime.datetime) -> str:
    if settings.get("useCustomDateTimeFormat"):
        try:
            return dt.strftime(settings.get("customDateTimeFormat"))
        except ValueError:
            return dt.strftime(Constants.DEFAULT_DATE_TIME_FORMAT)
    else:
        return dt.strftime(Constants.DEFAULT_DATE_TIME_FORMAT)


def uppercaseFirstLetter(text: str) -> str:
    """
    Only uppers the first letter of the string
    :param text: The String
    :return: The new string
    """
    if len(text) == 0:
        return ""

    return text[0].upper() + text[1:]


def getLexerStyles(lexer: "QsciLexer") -> dict[str, int]:
    styleDict = {}
    for name in dir(lexer):
        value = getattr(lexer, name)
        if isinstance(value, int):
            styleDict[name] = value
    return styleDict


def compareLists(firstList: list, secondList: list) -> bool:
    if len(firstList) != len(secondList):
        return False

    for i in firstList:
        if firstList.count(i) != secondList.count(i):
            return False

    return True


def getParentDirectory(path: str) -> str:
    return str(pathlib.Path(path).parent)


def findAllText(text: Union[str, bytes], pattern: Union[str, bytes]) -> list[int]:
    """
    Retruns a list of all positions of the pattern in the text
    """
    if len(text) == 0 or len(pattern) == 0:
        return []

    posList: list[int] = []
    currentPos = -1

    while True:
        pos = text.find(pattern)
        if pos == -1:
            break
        text = text[pos+1:]
        currentPos += pos + 1
        posList.append(currentPos)

    return posList