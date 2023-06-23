from PyQt6.QtWidgets import QMessageBox, QPushButton
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
import webbrowser
import tempfile
import zipfile
import urllib
import sys
import os


if TYPE_CHECKING:
    from jdTextEdit.gui.MainWindow import MainWindow
    from jdTextEdit.Environment import Environment


try:
    import requests
except ModuleNotFoundError:
    requests = None


# This cause problems when a new package from pip is needed
def installUpdates(parent: "MainWindow", env: "Environment", version: str):
    if os.access(env.programDir, os.W_OK):
        QMessageBox.critical(parent, QCoreApplication.translate("Updater", "No write permission"), QCoreApplication.translate("Updater", "You do not have write access to the installation folder. Please download the latest version by yourself."))
        webbrowser.open("https://sourceforge.net/projects/jdtextedit/files")
        return

    update_download_path = os.path.join(tempfile.gettempdir(), "jdTextEdit-Update.zip")
    try:
        urllib.request.urlretrieve("https://gitlab.com/JakobDev/jdTextEdit/-/archive/" + version + "/jdTextEdit-" + version + ".zip",update_download_path)
    except urllib.error.URLError:
        QMessageBox.critical(parent, QCoreApplication.translate("Updater", "No internet connection"), QCoreApplication.translate("Updater", "An Internet connection is required for this feature"))
    except Exception:
        QMessageBox.critical(parent, QCoreApplication.translate("Updater", "Unknown error"), QCoreApplication.translate("Updater", "An unknown error has occurred"))
    zip_file = zipfile.ZipFile(update_download_path)
    #Extract zip file
    for filename in zip_file.namelist():
        if filename.startswith("jdTextEdit-" + version + "/jdTextEdit/"):
            file_bytes = zip_file.read(filename)
            write_path = os.path.join(env.programDir, filename.removeprefix(f"jdTextEdit-{version}"))
            try:
                os.makedirs(os.path.dirname(write_path))
            except Exception:
                pass
            if os.path.isdir(write_path) or write_path.endswith("/"):
                continue
            with open(write_path, "wb") as f:
                f.write(file_bytes)
    zip_file.close()


def searchForUpdates(parent: "MainWindow", env: "Environment", startup: bool):
    if requests is None:
        if not startup:
            QMessageBox.critical(parent, QCoreApplication.translate("Updater", "requests not found"), QCoreApplication.translate("Updater", "This feature needs the Python requests module installed to work"))
        else:
            print(QCoreApplication.translate("Updater", "requests not found"), file=sys.stderr)
        return

    try:
        releaseList = requests.get("https://gitlab.com/api/v4/projects/14519914/releases").json()
    except requests.exceptions.RequestException:
        if startup:
            print(QCoreApplication.translate("Updater", "You need a internet connection to search for updates"))
        else:
            QMessageBox.critical(parent, QCoreApplication.translate("Updater", "No internet connection"), QCoreApplication.translate("Updater", "An Internet connection is required for this feature"))
        return
    except Exception as e:
        print(e)
        if not startup:
            QMessageBox.critical(parent, QCoreApplication.translate("Updater", "Unknown error"), QCoreApplication.translate("Updater", "An unknown error has occurred"))
        return
    if releaseList[0]["name"] != env.version:
        msgBox = QMessageBox()
        msgBox.setWindowTitle(QCoreApplication.translate("Updater", "New Version"))
        msgBox.setText(QCoreApplication.translate("Updater", "Version {{version}} of jdTextEdit is now aviable. Do you want do download it?").replace("{{version}}", releaseList[0]["name"]))
        msgBox.addButton(QPushButton(QCoreApplication.translate("Updater", "Yes")), QMessageBox.ButtonRole.YesRole)
        msgBox.addButton(QPushButton(QCoreApplication.translate("Updater", "No")), QMessageBox.ButtonRole.NoRole)
        answer = msgBox.exec()
        if answer == 0:
            webbrowser.open("https://sourceforge.net/projects/jdtextedit/files")
            #installUpdates(env,releaseList[0]["name"])
    elif not startup:
        QMessageBox.information(parent, QCoreApplication.translate("Updater", "No updates available"), QCoreApplication.translate("Updater", "There are currently no updates available. You are using the latest version."))
