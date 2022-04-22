from PyQt6.QtWidgets import QMessageBox, QWidget, QComboBox
from PyQt6.QtCore import Qt, QCoreApplication
from jdTextEdit.gui.CodeEdit import CodeEdit
from jdTextEdit.core.Project import Project
from typing import Dict, Any, Optional
from PyQt6.QtGui import QIcon
from pathlib import Path
import subprocess
import platform
import tempfile
import getpass
import shutil
import json
import sys
import re
import os


def getTemplates(path: str,templatelist: list):
    """
    Parses a template directory and stores it's content in a list
    :param path: directory
    :param templatelist: list
    """
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except:
            print(f"Could not create template directory {path}")
            return
    filelist = os.listdir(path)
    for i in filelist:
        templatePath = os.path.join(path,i)
        if os.path.isfile(templatePath):
            templatelist.append([i,templatePath])


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


def executeCommand(env, command: str,editWidget: CodeEdit,terminal: bool):
    """
    Executes a command. This function is used by the execute menu.
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
            pass
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


def getThemeIcon(env, name: str) -> QIcon:
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


def getDataPath(env) -> str:
    """
    Returns the Path to the data directory of jdTextEdit
    :param env: Enviroment
    :return: The Path
    """
    if env.args["dataDir"]:
        return getFullPath(env.args["dataDir"])
    elif os.getenv("JDTEXTEDIT_DATA_PATH"):
        return getFullPath(os.getenv("JDTEXTEDIT_DATA_PATH"))
    elif "dataDirectory" in env.distributionSettings:
        return getFullPath(env.distributionSettings["dataDirectory"])
    elif os.getenv("SNAP_USER_DATA"):
        return os.path.join(os.getenv("SNAP_USER_DATA"),"jdTextEdit")
    elif platform.system() == "Windows":
        return os.path.join(os.getenv("appdata"),"jdTextEdit")
    elif platform.system() == "Darwin":
        return os.path.join(str(Path.home()),"Library","Application Support","jdTextEdit")
    elif platform.system() == "Haiku":
        return os.path.join(str(Path.home()),"config","settings","jdTextEdit")
    else:
        if os.getenv("XDG_DATA_HOME"):
            return os.path.join(os.getenv("XDG_DATA_HOME"),"jdTextEdit")
        else:
            return os.path.join(str(Path.home()),".local","share","jdTextEdit")


def saveWindowState(window: QWidget, windict: dict, winid: str):
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


def restoreWindowState(window: QWidget,windict: dict,winid: str):
    """
    Retores a Window from the given dict
    :param window: The Window
    :param windict: The Dict
    :param winid: The ID of the Window
    """
    if winid in windict:
        window.setGeometry(windict[winid]["x"],windict[winid]["y"],windict[winid]["width"],windict[winid]["height"])
        if windict.get("maximized", False):
            window.setWindowState(Qt.WindowStates.WindowMaximized)


def getTempOpenFilePath() -> str:
    """
    Returns the path of the temporary file that is used for IPC
    :return: path
    """
    return os.path.join(tempfile.gettempdir(),"jdTextEdit_" + getpass.getuser() + ".tmp")


def selectComboBoxItem(comboBox: QComboBox, item: str):
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
            print(f"Can't parse {os.path.basename(path)}: {e.msg}: line {e.lineno} column {e.colno} (char {e.pos})", file=sys.stderr)
            return default
        except:
            print("Can't read " + os.path.basename(path), file=sys.stderr)
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
    if filename .find("/") == -1 and filename.find("\\") == -1:
        return True
    else:
        return False


def saveProjects(projectDict: Dict, path: str):
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


def loadProjects(env, path: str) -> Dict[str, Project]:
    """
    Loads the projetcs from a file
    :param env:
    :param path:
    :return:
    """
    data = readJsonFile(path, {})
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


def isRegExValid(regEx: str) -> bool:
    """
    Checks if a RegEx is valid
    :param regEx: The RegEx
    :return: valid
    """
    try:
        re.compile(regEx)
        return True
    except re.error:
        return False
