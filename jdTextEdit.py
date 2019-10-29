#!/usr/bin/env python3
from gui.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication
from Enviroment import Enviroment
from gui.CloseSaveWindow import CloseSaveWindow
from gui.SettingsWindow import SettingsWindow
from gui.SearchWindow import SearchWindow
from gui.SearchAndReplaceWindow import SearchAndReplaceWindow
from gui.GotoLineWindow import GotoLineWindow
from gui.DocumentStatistics import DocumentStatistics
from gui.DateTimeWindow import DateTimeWindow
from gui.ExecuteCommandWindow import ExecuteCommandWindow
from gui.EditCommandsWindow import EditCommandsWindow
from gui.DayTipWindow import DayTipWindow
from gui.AboutWindow import AboutWindow
from Functions import loadPlugins
import time
import sys
import os

from gui.SidebarWidgets.NotesWidget import NotesWidget
from gui.SidebarWidgets.TabListWidget import TabListWidget
from gui.SidebarWidgets.FileTreeWidget import FileTreeWidget
from gui.SidebarWidgets.ClipboardWidget import ClipboardWidget
from gui.SidebarWidgets.CharacterMapWidget import CharacterMapWidget

def main():
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
    env.editCommandsWindow = EditCommandsWindow(env)
    env.dayTipWindow = DayTipWindow(env)
    env.aboutWindow = AboutWindow(env)
    if env.settings.loadPlugins:
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

    env.mainWindow.setup()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
