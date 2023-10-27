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
def installUpdates(parent: "MainWindow", env: "Environment", zip_url: str) -> None:
    if os.access(env.programDir, os.W_OK):
        QMessageBox.critical(parent, QCoreApplication.translate("Updater", "No write permission"), QCoreApplication.translate("Updater", "You do not have write access to the installation folder. Please download the latest version by yourself."))
        webbrowser.open("https://sourceforge.net/projects/jdtextedit/files")
        return

    update_download_path = os.path.join(tempfile.gettempdir(), "jdTextEdit-Update.zip")
    try:
        urllib.request.urlretrieve(zip_url, update_download_path)
    except urllib.error.URLError:
        QMessageBox.critical(parent, QCoreApplication.translate("Updater", "No internet connection"), QCoreApplication.translate("Updater", "An Internet connection is required for this feature"))
    except Exception:
        QMessageBox.critical(parent, QCoreApplication.translate("Updater", "Unknown error"), QCoreApplication.translate("Updater", "An unknown error has occurred"))
    zip_file = zipfile.ZipFile(update_download_path)
    #Extract zip file
    for filename in zip_file.namelist():
        if filename.startswith("jdtextedit/jdTextEdit"):
            file_bytes = zip_file.read(filename)
            write_path = os.path.join(env.programDir, filename.removeprefix(f"jdtextedit"))
            try:
                os.makedirs(os.path.dirname(write_path))
            except Exception:
                pass
            if os.path.isdir(write_path) or write_path.endswith("/"):
                continue
            with open(write_path, "wb") as f:
                f.write(file_bytes)
    zip_file.close()


def searchForUpdates(parent: "MainWindow", env: "Environment", startup: bool) -> None:
    if requests is None:
        if not startup:
            QMessageBox.critical(parent, QCoreApplication.translate("Updater", "requests not found"), QCoreApplication.translate("Updater", "This feature needs the Python requests module installed to work"))
        else:
            env.logger.critical(QCoreApplication.translate("Updater", "requests not found"))
        return

    try:
        latestRelease = requests.get("https://codeberg.org/api/v1/repos/JakobDev/jdTextEdit/releases/latest").json()
    except requests.exceptions.RequestException:
        if startup:
            env.logger.error(QCoreApplication.translate("Updater", "You need a internet connection to search for updates"))
        else:
            QMessageBox.critical(parent, QCoreApplication.translate("Updater", "No internet connection"), QCoreApplication.translate("Updater", "An Internet connection is required for this feature"))
        return
    except Exception as ex:
        env.logger.exception(ex)
        if not startup:
            QMessageBox.critical(parent, QCoreApplication.translate("Updater", "Unknown error"), QCoreApplication.translate("Updater", "An unknown error has occurred"))
        return
    if latestRelease["name"] != env.version:
        msgBox = QMessageBox()
        msgBox.setWindowTitle(QCoreApplication.translate("Updater", "New Version"))
        msgBox.setText(QCoreApplication.translate("Updater", "Version {{version}} of jdTextEdit is now aviable. Do you want do download it?").replace("{{version}}", latestRelease["name"]))
        msgBox.addButton(QPushButton(QCoreApplication.translate("Updater", "Yes")), QMessageBox.ButtonRole.YesRole)
        msgBox.addButton(QPushButton(QCoreApplication.translate("Updater", "No")), QMessageBox.ButtonRole.NoRole)
        answer = msgBox.exec()
        if answer == 0:
            webbrowser.open("https://sourceforge.net/projects/jdtextedit/files")
            #installUpdates(env, latestRelease["zipball_url"])
    elif not startup:
        QMessageBox.information(parent, QCoreApplication.translate("Updater", "No updates available"), QCoreApplication.translate("Updater", "There are currently no updates available. You are using the latest version."))
