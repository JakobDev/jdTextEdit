from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from pathlib import Path
import subprocess
import importlib
import traceback
import platform
import tempfile
import getpass
import json
import sys
import os

def loadPlugins(path,env):
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
        try:
            p = importlib.import_module(i)
            plugid = p.getID()
            #Just to make sure these functions exists
            p.getName()
            p.getVersion()
            p.getAuthor()
            env.plugins[plugid] = p
            if not plugid in env.settings.disabledPlugins:
                env.plugins[plugid].main(env)
        except Exception as e:
            print(traceback.format_exc(),end="")

def getTemplates(path,templatelist):
    if not os.path.isdir(path):
        os.mkdir(path)
    filelist = os.listdir(path)
    for i in filelist:
        templatelist.append([i,os.path.join(path,i)])
    return templatelist

def executeCommand(command,editWidget,terminal):
    command = command.replace("%url%","file://" + editWidget.getFilePath())
    command = command.replace("%path%",editWidget.getFilePath())
    command = command.replace("%directory%",os.path.dirname(editWidget.getFilePath()))
    command = command.replace("%filename%",os.path.basename(editWidget.getFilePath()))
    command = command.replace("%selection%",editWidget.selectedText())
    if terminal:
        if platform.system() == 'Windows':
            subprocess.Popen(["cmd.exe","/C",command])
            pass
        elif platform.system() == 'Darwin':
            #subprocess.call(('open', filepath))
            pass
        elif os.getenv("SNAP"):
            subprocess.Popen([os.path.join(os.getenv("SNAP"),"usr","bin","xterm"),"-e",command])
        else:
            subprocess.Popen(["x-terminal-emulator","-e",command])
    else:
        os.popen(command)

def getThemeIcon(env,name):
    if QIcon.themeName() and env.settings.useNativeIcons:
        return QIcon.fromTheme(name)
    else:
        return QIcon(os.path.join(env.programDir,"icons/" + name + ".png"))

def openFileDefault(filepath):
    if platform.system() == 'Windows':
        os.startfile(filepath)
    elif platform.system() == 'Darwin':
        subprocess.call(('open', filepath))
    else:
        subprocess.call(('xdg-open', filepath))

def showMessageBox(title, text):
    messageBox = QMessageBox()
    messageBox.setWindowTitle(title)
    messageBox.setText(text)
    messageBox.setStandardButtons(QMessageBox.Ok)
    messageBox.exec_()

def getDataPath(env):
    if env.args["dataDir"]:
        return env.args["dataDir"]
    elif os.getenv("JDTEXTEDIT_DATA_PATH"):
        return os.getenv("JDTEXTEDIT_DATA_PATH")
    elif "dataDirectory" in env.distributionSettings:
        return env.distributionSettings["dataDirectory"].replace("~",str(Path.home()))
    elif os.getenv("SNAP_USER_DATA"):
        return os.path.join(os.getenv("SNAP_USER_DATA"),"jdTextEdit")
    elif platform.system() == 'Windows':
        return os.path.join(os.getenv("appdata"),"jdTextEdit")
    elif platform.system() == 'Darwin':
        return os.path.join(str(Path.home()),"Library","Application Support","jdTextEdit")
    else:
        if os.getenv("XDG_DATA_HOME"):
            return os.path.join(os.getenv("XDG_DATA_HOME"),"jdTextEdit")
        else:
            return os.path.join(str(Path.home()),".local","share","jdTextEdit")

def saveWindowState(window,windict,winid):
    windict[winid] = {}
    x,y,w,h = window.geometry().getRect()
    windict[winid]["x"] = x
    windict[winid]["y"] = y
    windict[winid]["width"] = w
    windict[winid]["height"] = h

def restoreWindowState(window,windict,winid):
    if winid in windict:
        window.setGeometry(windict[winid]["x"],windict[winid]["y"],windict[winid]["width"],windict[winid]["height"])

def getTempOpenFilePath():
    return os.path.join(tempfile.gettempdir(),"jdTextEdit_" + getpass.getuser() + ".tmp")

def selectComboBoxItem(comboBox, item):
    for i in range(comboBox.count()):
        if comboBox.itemText(i) == item:
            comboBox.setCurrentIndex(i)

def readJsonFile(path,default):
    if os.path.isfile(path):
        try:
            with open(path,"r",encoding="utf-8") as f:
                data = json.load(f)
                return data
        except:
            print("Can't read " + os.path.basename(path))
            return default
    else:
        return default
