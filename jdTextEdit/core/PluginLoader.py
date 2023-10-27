from PyQt6.QtWidgets import QMessageBox, QApplication, QSplashScreen
from jdTextEdit.Functions import readJsonFile
from PyQt6.QtCore import QCoreApplication
from typing import Any, TYPE_CHECKING
import subprocess
import importlib
import traceback
import platform
import sys
import os


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


def shouldPluginLoaded(manifest: dict[str, Any]) -> bool:
    """Checks if a Plugin allows loading it on the System"""
    if "only" not in manifest:
        return True
    if "system" in manifest["only"] and platform.system() not in manifest["only"]["system"]:
        return False
    return True


def installPipPackages(env: "Environment", packageList: list[str], pluginName: str):
    missingPackages = []
    for i in packageList:
        if not importlib.util.find_spec(i):
            missingPackages.append(i)

    if len(missingPackages) == 0:
        return

    answer = QMessageBox.question(None, QCoreApplication.translate("PluginLoader", "Additional Packages required"), QCoreApplication.translate("PluginLoader", "{{plugin}} requires some additional packages. Do you want to install them?").replace("{{plugin}}", pluginName))
    if answer != QMessageBox.StandardButton.Yes:
        return

    w = QSplashScreen()
    w.show()
    w.showMessage(QCoreApplication.translate("PluginLoader", "Installing packages...<br>This may take some time", "The <br> marks a line break"))
    QApplication.processEvents()
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install"] + missingPackages)
    except FileNotFoundError:
        w.close()
        QMessageBox.critical(None, QCoreApplication.translate("PluginLoader", "Pip not found"), QCoreApplication.translate("PluginLoader", "Pip was not found"))
        return

    w.close()
    if result.returncode != 0:
        QMessageBox.critical(None, QCoreApplication.translate("PluginLoader", "Instalation failed"), QCoreApplication.translate("PluginLoader", "The instalation of the packages failed"))


def loadSinglePlugin(pluginDir: str, env: "Environment") -> bool:
    env.logger.debug(f"Loading plugin from {pluginDir}")

    if not os.path.isdir(pluginDir):
        env.logger.critical(QCoreApplication.translate("PluginLoader", "Directory {{path}} does not exists").replace("{{path}}", pluginDir))
        return False

    manifest_path = os.path.join(pluginDir, "manifest.json")
    if not os.path.isfile(manifest_path):
        env.logger.critical(QCoreApplication.translate("PluginLoader", "{{path}} has no manifest.json").replace("{{path}}", pluginDir))
        return False

    manifest_data = readJsonFile(manifest_path, None)
    if not manifest_data:
        return False

    for i in ("id", "name", "version", "author"):
        if i not in manifest_data:
            env.logger.critical(QCoreApplication.translate("PluginLoader", "{{path}} has no key {{key}}").replace("{{path}}", manifest_path).replace("{{key}}", i))
            return False

    manifest_data["version"] = manifest_data["version"].replace("{JDTEXTEDIT_VERSION}", env.version)
    if not shouldPluginLoaded(manifest_data):
        env.logger.info(QCoreApplication.translate("PluginLoader", "Skipping loading of Plugin {{id}}").replace("{{id}}", manifest_data["id"]))
        return False

    plugin_id = manifest_data["id"]
    if plugin_id in env.settings.get("disabledPlugins"):
        env.logger.info(QCoreApplication.translate("PluginLoader", "Plugin {{plugin}} is disabled. Skipping loading").replace("{{plugin}}", plugin_id))
        return False

    if plugin_id in env.plugins:
        env.logger.error(QCoreApplication.translate("PluginLoader", "A Plugin with ID {{id}} is already loaded").replace("{{id}}", plugin_id))
        return False

    if "requirements" in manifest_data:
        installPipPackages(env, manifest_data["requirements"], manifest_data["name"])
    try:
        p = importlib.import_module(os.path.basename(pluginDir))
        env.plugins[plugin_id] = manifest_data
        env.plugins[plugin_id]["module"] = p
    except Exception as e:
        env.logger.exception(e)
        return False

    env.plugins[plugin_id]["module"].main(env)
    return True


def loadPlugins(path: str, env: "Environment") -> None:
    """
    Loads a Plugin for jdTextEdit
    :param path: plugin
    :param env: Enviroment
    """
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except Exception:
            return

    pluginlist = os.listdir(path)
    sys.path.append(path)
    for i in pluginlist:
        if i == "__init__.py" or i == "__pycache__":
            continue
        loadSinglePlugin(os.path.join(path, i), env)
