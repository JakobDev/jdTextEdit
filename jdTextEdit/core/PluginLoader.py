from PyQt6.QtWidgets import QMessageBox, QApplication, QSplashScreen
from jdTextEdit.Functions import readJsonFile
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
    answer = QMessageBox.question(None, env.translate("installPackages.title"), env.translate("installPackages.text").replace("{pluginName}", pluginName))
    if answer != QMessageBox.StandardButton.Yes:
        return
    w = QSplashScreen()
    w.show()
    w.showMessage("Installing packages.<br> This may take some time")
    QApplication.processEvents()
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install"] + missingPackages)
    except FileNotFoundError:
        w.close()
        QMessageBox.critical(None, "Pip not found", "Pip was not found")
        return
    w.close()
    if result.returncode != 0:
        QMessageBox.critical(None, env.translate("pipFailed.title"), env.translate("pipFailed.text"))


def loadSinglePlugin(pluginDir: str, env) -> bool:
    if not os.path.isdir(pluginDir):
        print(f"Directory {pluginDir} does not exists", file=sys.stderr)
        return False
    manifest_path = os.path.join(pluginDir, "manifest.json")
    if not os.path.isfile(manifest_path):
        print(pluginDir + " has no manifest.json", file=sys.stderr)
        return False
    manifest_data = readJsonFile(manifest_path, None)
    if not manifest_data:
        return False
    for i in ("id", "name", "version", "author"):
        if i not in manifest_data:
            print(f"{manifest_path} has no key {i}", file=sys.stderr)
            return False
    manifest_data["version"] = manifest_data["version"].replace("{JDTEXTEDIT_VERSION}", env.version)
    if not shouldPluginLoaded(manifest_data):
        print(f"Skipping loading of Plugin " + manifest_data["id"])
        return False
    plugin_id = manifest_data["id"]
    if plugin_id in env.settings.get("disabledPlugins"):
        return False
    if plugin_id in env.plugins:
        print(f"A Plugin with ID {plugin_id} is already loaded", file=sys.stderr)
        return False
    if "requirements" in manifest_data:
        installPipPackages(env, manifest_data["requirements"], manifest_data["name"])
    try:
        p = importlib.import_module(os.path.basename(pluginDir))
        env.plugins[plugin_id] = manifest_data
        env.plugins[plugin_id]["module"] = p
    except Exception as e:
        print(traceback.format_exc(), end="", file=sys.stderr)
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
