#!/usr/bin/env python3
from gui.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication
from SharedEnviroment import SharedEnviroment
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

app = QApplication(sys.argv)
env = SharedEnviroment()
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

env.mainWindow.setup()
env.mainWindow.show()
sys.exit(app.exec_())
