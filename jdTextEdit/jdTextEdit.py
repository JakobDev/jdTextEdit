from jdTextEdit.gui.Tools.RegExGrep.RegExGrepWindow import RegExGrepWindow
from jdTextEdit.gui.SearchAndReplaceWindow import SearchAndReplaceWindow
from jdTextEdit.core.PluginLoader import loadPlugins, loadSinglePlugin
from jdTextEdit.gui.StatusBarWidgets import addBuiltinStatusBarWidgets
from jdTextEdit.gui.ExecuteCommandWindow import ExecuteCommandWindow
from jdTextEdit.Functions import getTempOpenFilePath, compareLists
from PyQt6.QtWidgets import QApplication, QMessageBox, QCheckBox
from jdTextEdit.gui.DocumentStatistics import DocumentStatistics
from jdTextEdit.gui.ManageMacrosWindow import ManageMacrosWindow
from jdTextEdit.gui.EditCommandsWindow import EditCommandsWindow
from jdTextEdit.gui.ActionSearchWindow import ActionSearchWindow
from jdTextEdit.core.Logger import setupLogger, getGlobalLogger
from jdTextEdit.gui.AddProjectWindow import AddProjectWindow
from jdTextEdit.gui.CloseSaveWindow import CloseSaveWindow
from jdTextEdit.gui.DebugInfoWindow import DebugInfoWindow
from jdTextEdit.gui.SettingsWindow import SettingsWindow
from jdTextEdit.gui.GotoLineWindow import GotoLineWindow
from jdTextEdit.gui.DateTimeWindow import DateTimeWindow
from jdTextEdit.gui.SearchWindow import SearchWindow
from jdTextEdit.gui.DayTipWindow import DayTipWindow
from jdTextEdit.gui.AboutWindow import AboutWindow
from jdTextEdit.gui.MainWindow import MainWindow
from jdTextEdit.Environment import Environment
from jdTextEdit.Constants import Constants
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon
import importlib
import platform
import tempfile
import argparse
import ctypes
import json
import glob
import time
import sys
import os

from jdTextEdit.gui.SidebarWidgets.NotesWidget import NotesWidget
from jdTextEdit.gui.SidebarWidgets.TabListWidget import TabListWidget
from jdTextEdit.gui.SidebarWidgets.FileTreeWidget import FileTreeWidget
from jdTextEdit.gui.SidebarWidgets.ClipboardWidget import ClipboardWidget
from jdTextEdit.gui.SidebarWidgets.CharacterMapWidget import CharacterMapWidget
from jdTextEdit.gui.SidebarWidgets.ProjectWidget import ProjectWidget


def checkOptionalModules(env: Environment):
    notFoundModules = []

    for i in ("lxml", "editorconfig", "requests", Constants.DEFAULT_ENCODING_DETECT_LIB):
        try:
            importlib.import_module(i)
        except ModuleNotFoundError:
            notFoundModules.append(i)

    if len(notFoundModules) == 0 or compareLists(notFoundModules, env.settings.get("optionalModulesWarningWhitelist", [])):
        return

    text = QCoreApplication.translate("jdTextEdit", "The following optional Python modules are missing:") + "<br>"
    for i in notFoundModules:
        text += i + "<br>"
    text += "<br>" + QCoreApplication.translate("jdTextEdit", "jdTextEdit will run without this modules, but some features are not working. You probably want to install them.")

    messageBox = QMessageBox()
    checkBox = QCheckBox(QCoreApplication.translate("jdTextEdit", "Don't show this again"))

    messageBox.setCheckBox(checkBox)
    messageBox.setWindowTitle(QCoreApplication.translate("jdTextEdit", "Missing optional modules"))
    messageBox.setText(text)

    messageBox.exec()

    if checkBox.isChecked():
        env.settings.set("optionalModulesWarningWhitelist", notFoundModules)
    else:
        env.settings.set("optionalModulesWarningWhitelist", [])


def _handleWindowsForeground(temp_open_path: str) -> None:
    """
    On Windows Programs can't bring themself into focus, so we must do that here.
    This only works, if jdTextEdit is luanched with pythonw."
    """
    file_handle, wid_path = tempfile.mkstemp(prefix="jdTextEditWindowID_")
    os.close(file_handle)

    with open(temp_open_path, "w", encoding="utf-8") as f:
        json.dump({"action": "writeWindowID", "file": wid_path}, f)

    time.sleep(0.5)

    if os.path.getsize(wid_path) != 0:
        try:
            with open(wid_path, "r", encoding="utf-8") as f:
                wid = int(f.read().strip())
                ctypes.windll.user32.SetForegroundWindow(wid)
        except Exception as e:
            getGlobalLogger().exception(e)

    os.remove(wid_path)


def _writeTempFile(temp_open_path: str, args: argparse.Namespace) -> None:
    if platform.system() == "Windows":
        _handleWindowsForeground(temp_open_path)

    with open(temp_open_path, "w", encoding="utf-8") as f:
        json.dump({"action": "openFile", "path": [os.path.abspath(i) for i in args.path]}, f)

    time.sleep(0.5)
    if os.path.getsize(temp_open_path) == 0:
        sys.exit(0)
    else:
        os.remove(temp_open_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="*")
    parser.add_argument("-p", "--portable",action="store_true", dest="portable", help="Portable")
    parser.add_argument("--data-dir", dest="dataDir",help="Sets the data directory")
    parser.add_argument("--disable-plugins", action="store_true", dest="disablePlugins", help="Disable Plugins")
    parser.add_argument("--no-session-restore", action="store_true", dest="disableSessionRestore", help="Disable Session Restore")
    parser.add_argument("--disable-updater", action="store_true", dest="disableUpdater", help="Disable the Updater")
    parser.add_argument("--distribution-file", dest="distributionFile", help="Sets custom distribution.json")
    parser.add_argument("--language", dest="language", help="Starts jdTextEdit in the given language")
    parser.add_argument("--debug", action="store_true", dest="debug", help="Enable Debug mode")
    parser.add_argument("--debug-plugin", dest="debugPlugin", help="Loads a single Plugin from a directory")
    parser.add_argument("--log-format", choices=["default", "no-color", "unformatted"], dest="logFormat", default="default", help="Set the format for the log messages")
    parser.add_argument("--log-file", dest="logFile", help="Write the log in this file")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", help="Print more messages")
    args = parser.parse_known_args()[0]

    setupLogger(args.debug, args.logFormat, args.verbose, args.logFile)

    temp_open_path = getTempOpenFilePath()
    if os.path.isfile(temp_open_path):
        _writeTempFile(temp_open_path, args)

    app = QApplication(sys.argv)

    app.setApplicationName("jdTextEdit")
    app.setDesktopFileName("page.codeberg.JakobDev.jdTextEdit")

    env = Environment(app, args.__dict__)

    if not env.debugMode and env.distributionSettings.get("enableTranslationWarning", True) and len(glob.glob(os.path.join(env.programDir, "translations", "*.qm"))) == 0:
        env.logger.warning("No translations found")
        QMessageBox.warning(None, "No translations found", "No translation were found. It looks like the translations of jdTextEdit were not build. jdTextEdit is currently only available in English.")

    env.clipboard = QApplication.clipboard()
    env.closeSaveWindow = CloseSaveWindow(env)
    env.searchWindow = SearchWindow(env)
    env.searchReplaceWindow = SearchAndReplaceWindow(env)
    env.gotoLineWindow = GotoLineWindow(env)
    env.documentStatistics = DocumentStatistics(env)
    env.dateTimeWindow = DateTimeWindow(env)
    env.executeCommandWindow = ExecuteCommandWindow(env)
    env.mainWindow = MainWindow(env)
    env.settingsWindow = SettingsWindow(env)
    env.manageMacrosWindow = ManageMacrosWindow(env)
    env.editCommandsWindow = EditCommandsWindow(env)
    env.dayTipWindow = DayTipWindow(env)
    env.actionSearchWindow = ActionSearchWindow(env)
    env.aboutWindow = AboutWindow(env)
    env.addProjectWindow = AddProjectWindow(env)
    env.regExGrepWindow = RegExGrepWindow(env)
    env.debugInfoWindow = DebugInfoWindow(env)
    if env.settings.get("loadPlugins") and not env.args["disablePlugins"]:
        loadPlugins(os.path.join(env.programDir, "plugins"), env)
        loadPlugins(os.path.join(env.dataDir, "plugins"), env)
        if env.args["debugPlugin"]:
            loadSinglePlugin(env.args["debugPlugin"], env)

    env.pluginAPI.addSidebarWidget(NotesWidget())
    env.pluginAPI.addSidebarWidget(TabListWidget(env))
    env.pluginAPI.addSidebarWidget(FileTreeWidget(env))
    env.pluginAPI.addSidebarWidget(ClipboardWidget())
    env.pluginAPI.addSidebarWidget(CharacterMapWidget(env))
    env.pluginAPI.addSidebarWidget(ProjectWidget(env))

    addBuiltinStatusBarWidgets(env)

    if os.path.isfile(os.path.join(env.dataDir, "userChrome.css")) and env.settings.get("enableUserChrome"):
        f = open(os.path.join(env.dataDir, "userChrome.css"), "r", encoding="utf-8")
        app.setStyleSheet(f.read())
        f.close()

    app.setWindowIcon(QIcon(os.path.join(env.programDir, "Logo.svg")))

    checkOptionalModules(env)

    # Ask for automatic updates on first run
    if env.firstRun and env.enableUpdater:
        answer = QMessageBox.question(env.mainWindow, QCoreApplication.translate("jdTextEdit", "Enable automatic update search"), QCoreApplication.translate("jdTextEdit", "jdTextEdit offers the possibility to automatically check for updates every time the programme is started. Do you want to activate this? You can change this behaviour later in the settings."))

        if answer == QMessageBox.StandardButton.Yes:
            env.settings.set("searchUpdates", True)
        else:
            env.settings.set("searchUpdates", False)

    env.mainWindow.setup()
    sys.exit(app.exec())
