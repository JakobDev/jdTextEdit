from PyQt5.QtWidgets import QMessageBox, QPushButton
from jdTextEdit.Functions import showMessageBox
import webbrowser
import requests
import os

def searchForUpdates(env,startup):
    if os.getenv("SNAP"):
        if not startup:
            showMessageBox(env.translate("updater.snap.title"),env.translate("updater.snap.text"))
        return
    try:
        releaseList = requests.get("https://gitlab.com/api/v4/projects/14519914/releases").json()
    except requests.exceptions.RequestException:
        if startup:
            print("You need a internet connection to search for updates")
        else:
            showMessageBox(env.translate("noInternetConnection.title"),env.translate("noInternetConnection.text"))
        return
    except Exception as e:
        print(e)
        if not startup:
            showMessageBox(env.translate("unknownError.title"),env.translate("unknownError.text"))
        return
    if releaseList[0]["name"] != env.version:
        msgBox = QMessageBox()
        msgBox.setWindowTitle(env.translate("updater.newVersion.title"))
        msgBox.setText(env.translate("updater.newVersion.text") % releaseList[0]["name"])
        msgBox.addButton(QPushButton(env.translate("button.yes")), QMessageBox.YesRole)
        msgBox.addButton(QPushButton(env.translate("button.no")), QMessageBox.NoRole)
        answer = msgBox.exec_()
        if answer == 0:
            webbrowser.open("https://gitlab.com/JakobDev/jdTextEdit/-/releases/")
    elif not startup:
        showMessageBox(env.translate("updater.noUpdates.title"),env.translate("updater.noUpdates.text"))
