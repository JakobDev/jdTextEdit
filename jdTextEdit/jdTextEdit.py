from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox, QCheckBox
from jdTextEdit.gui.MainWindow import MainWindow
from jdTextEdit.Environment import Environment
from jdTextEdit.gui.CloseSaveWindow import CloseSaveWindow
from jdTextEdit.gui.SettingsWindow import SettingsWindow
from jdTextEdit.gui.SearchWindow import SearchWindow
from jdTextEdit.gui.SearchAndReplaceWindow import SearchAndReplaceWindow
from jdTextEdit.gui.GotoLineWindow import GotoLineWindow
from jdTextEdit.gui.DocumentStatistics import DocumentStatistics
from jdTextEdit.gui.DateTimeWindow import DateTimeWindow
from jdTextEdit.gui.ExecuteCommandWindow import ExecuteCommandWindow
from jdTextEdit.gui.ManageMacrosWindow import ManageMacrosWindow
from jdTextEdit.gui.EditCommandsWindow import EditCommandsWindow
from jdTextEdit.gui.DayTipWindow import DayTipWindow
from jdTextEdit.gui.ActionSearchWindow import ActionSearchWindow
from jdTextEdit.gui.AboutWindow import AboutWindow
from jdTextEdit.gui.AddProjectWindow import AddProjectWindow
from jdTextEdit.gui.Tools.RegExGrep.RegExGrepWindow import RegExGrepWindow
from jdTextEdit.gui.DebugInfoWindow import DebugInfoWindow
from jdTextEdit.Functions import getTempOpenFilePath, compareLists
from jdTextEdit.core.PluginLoader import loadPlugins, loadSinglePlugin
from jdTextEdit.gui.StatusBarWidgets import addBuiltinStatusBarWidgets
from jdTextEdit.Constants import Constants
from PyQt6.QtCore import QCoreApplication
import importlib
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


def main():
    temp_open_path = getTempOpenFilePath()
    if os.path.isfile(temp_open_path):
        with open(temp_open_path, "w") as f:
            if len(sys.argv) == 2:
                f.write("openFile" + "\n" + os.path.abspath(sys.argv[1]))
            else:
                f.write("focus")
        time.sleep(0.5)
        if os.path.getsize(temp_open_path) == 0:
            sys.exit(0)
        else:
            os.remove(temp_open_path)

    app = QApplication(sys.argv)

    app.setApplicationName("jdTextEdit")
    app.setDesktopFileName("page.codeberg.JakobDev.jdTextEdit")

    env = Environment(app)

    if not env.debugMode and env.distributionSettings.get("enableTranslationWarning", True) and len(glob.glob(os.path.join(env.programDir, "translations", "*.qm"))) == 0:
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
