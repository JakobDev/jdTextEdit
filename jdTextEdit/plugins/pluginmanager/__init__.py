from .PluginManagerWindow import PluginManagerWindow
from PyQt5.QtWidgets import QAction
import os

def main(env):
    currentDir = os.path.dirname(os.path.realpath(__file__))
    env.translations.loadDirectory(os.path.join(currentDir,"translation"))
    env.pluginManagerWindow = PluginManagerWindow(env)
    
    openPluginManager = QAction(env.translate("pluginManagerWindow.title"),env.mainWindow)
    openPluginManager.triggered.connect(env.pluginManagerWindow.openWindow)
    openPluginManager.setData(["openPluginManager"])
    env.mainWindow.editMenu.addAction(openPluginManager)

def getID():
    return "pluginmanager"

def getVersion():
    return "1.0"

def getName():
    return "Pluginmanager"

def getAuthor():
    return "JakobDev"
