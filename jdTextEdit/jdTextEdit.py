#!/usr/bin/env python3
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from jdTextEdit.gui.MainWindow import MainWindow
from jdTextEdit.Enviroment import Enviroment
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
from jdTextEdit.gui.AboutWindow import AboutWindow
from jdTextEdit.Functions import loadPlugins, getTempOpenFilePath
import time
import sys
import os

from jdTextEdit.gui.SidebarWidgets.NotesWidget import NotesWidget
from jdTextEdit.gui.SidebarWidgets.TabListWidget import TabListWidget
from jdTextEdit.gui.SidebarWidgets.FileTreeWidget import FileTreeWidget
from jdTextEdit.gui.SidebarWidgets.ClipboardWidget import ClipboardWidget
from jdTextEdit.gui.SidebarWidgets.CharacterMapWidget import CharacterMapWidget

def main():
    temp_open_path = getTempOpenFilePath()
    if os.path.isfile(temp_open_path):
        with open(temp_open_path,"w") as f:
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
    env = Enviroment()
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
    env.aboutWindow = AboutWindow(env)
    if env.settings.loadPlugins and not env.args["disablePlugins"]:
        loadPlugins(os.path.join(env.programDir,"plugins"),env)
        loadPlugins(os.path.join(env.dataDir,"plugins"),env)

    env.dockWidgtes.append([NotesWidget(env),env.translate("sidebar.notes"),"notes"])
    env.dockWidgtes.append([TabListWidget(env),env.translate("sidebar.tabs"),"tablist"])
    env.dockWidgtes.append([FileTreeWidget(env),env.translate("sidebar.files"),"files"])
    env.dockWidgtes.append([ClipboardWidget(env),env.translate("sidebar.clipboard"),"clipboard"])
    env.dockWidgtes.append([CharacterMapWidget(env),env.translate("sidebar.charactermap"),"charactermap"])

    if os.path.isfile(os.path.join(env.dataDir,"userChrome.css")):
        f = open(os.path.join(env.dataDir,"userChrome.css"),"r",encoding="utf-8")
        app.setStyleSheet(f.read())
        f.close()

    app.setWindowIcon(QIcon(os.path.join(env.programDir,"Logo.png")))

    env.mainWindow.setup()
    sys.exit(app.exec())
