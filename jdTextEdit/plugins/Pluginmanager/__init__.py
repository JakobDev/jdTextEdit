from .PluginManagerWindow import PluginManagerWindow
from typing import TYPE_CHECKING
from PyQt6.QtGui import QAction
import os


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


def main(env: "Environment") -> None:
    currentDir = os.path.dirname(os.path.realpath(__file__))
    env.translations.loadDirectory(os.path.join(currentDir, "translations"))
    env.pluginManagerWindow = PluginManagerWindow(env)

    openPluginManager = QAction(env.translate("pluginManagerWindow.title"), env.mainWindow)
    openPluginManager.triggered.connect(env.pluginManagerWindow.openWindow)
    openPluginManager.setData(["openPluginManager"])
    env.mainWindow.editMenu.addAction(openPluginManager)
