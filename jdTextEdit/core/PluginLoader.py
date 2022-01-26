from PyQt6.QtWidgets import QMessageBox, QLabel, QApplication, QSplashScreen
from PyQt6.QtCore import QProcess, QThread
from jdTextEdit.Functions import readJsonFile
from typing import List, NoReturn
import subprocess
import importlib
import traceback
import sys
import os


def installPipPackages(env, packageList: List[str], pluginName: str):
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
        result = subprocess.run(["pip", "install"] + missingPackages)
    except FileNotFoundError:
        w.close()
        QMessageBox.critical(None, "Pip not found", "Pip was not found")
        return
    w.close()
    if result.returncode != 0:
        QMessageBox.critical(None, env.translate("pipFailed.title"), env.translate("pipFailed.text"))


def loadSinglePlugin(dir: str, env) -> bool:
    if not os.path.isdir(dir):
        print(f"Directory {dir} does not exists", file=sys.stderr)
        return False
    manifest_path = os.path.join(dir, "manifest.json")
    if not os.path.isfile(manifest_path):
        print(dir + " has no manifest.json", file=sys.stderr)
        return False
    manifest_data = readJsonFile(manifest_path, None)
    if not manifest_data:
        return False
    for i in ("id", "name", "version", "author"):
        if i not in manifest_data:
            print(f"{manifest_path} has no key {i}", file=sys.stderr)
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
        p = importlib.import_module(os.path.basename(dir))
        env.plugins[plugin_id] = manifest_data
        env.plugins[plugin_id]["module"] = p
        env.plugins[plugin_id]["module"].main(env)
    except Exception as e:
        print(traceback.format_exc(), end="", file=sys.stderr)
        return False
    return True


def loadPlugins(path: str, env) -> NoReturn:
    """
    Loads a Plugin for jdTextEdit
    :param path: plugin
    :param env: Enviroment
    """
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except:
            return
    pluginlist = os.listdir(path)
    sys.path.append(path)
    for i in pluginlist:
        if i == "__init__.py" or i == "__pycache__":
            continue
        loadSinglePlugin(os.path.join(path, i), env)