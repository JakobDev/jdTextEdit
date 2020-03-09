from PyQt5.QtWidgets import QMessageBox, QPushButton
from jdTextEdit.Functions import showMessageBox
import webbrowser
import tempfile
import requests
import zipfile
import urllib
import os

#This cause problems when a new package from pip is needed
def installUpdates(env,version):
    if os.access(env.programDir,os.W_OK):
        showMessageBox(env.translate("updater.readOnly.title"),env.translate("updater.readOnly.text"))
        webbrowser.open("https://sourceforge.net/projects/jdtextedit/files")
        return
    update_download_path = os.path.join(tempfile.gettempdir(),"jdTextEdit-Update.zip")
    try:
        urllib.request.urlretrieve("https://gitlab.com/JakobDev/jdTextEdit/-/archive/" + version + "/jdTextEdit-" + version + ".zip",update_download_path)
    except urllib.error.URLError:
        showMessageBox(env.translate("noInternetConnection.title"),env.translate("noInternetConnection.text"))
    except:
        showMessageBox(env.translate("unknownError.title"),env.translate("unknownError.text"))
    zip_file = zipfile.ZipFile(update_download_path)
    #Extract zip file
    for filename in zip_file.namelist():
        if filename.startswith("jdTextEdit-" +  version + "/jdTextEdit/"):
            file_bytes = zip_file.read(filename)
            write_path = os.path.join(env.programDir,filename[23+len(version):])
            try:
                os.makedirs(os.path.dirname(write_path))
            except:
                pass
            if os.path.isdir(write_path) or write_path.endswith("/"):
                continue
            with open(write_path,"wb") as f:
                f.write(file_bytes)
    zip_file.close()

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
            webbrowser.open("https://sourceforge.net/projects/jdtextedit/files")
            #installUpdates(env,releaseList[0]["name"])
    elif not startup:
        showMessageBox(env.translate("updater.noUpdates.title"),env.translate("updater.noUpdates.text"))
