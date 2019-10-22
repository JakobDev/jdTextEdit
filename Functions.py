from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from pathlib import Path
import subprocess
import importlib
import traceback
import platform
import sys
import os

def loadPlugins(path,env):
    if not os.path.isdir(path):
        if not os.access(path,os.W_OK):
            return
        else:
            os.mkdir(path)
    pluginlist = os.listdir(path)
    sys.path.append(path)
    for i in pluginlist:
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

def executeCommand(command,selectedTab,terminal):
    command = command.replace("%url%","file://" + selectedTab[1])
    command = command.replace("%path%",selectedTab[1])
    command = command.replace("%directory%",os.path.dirname(selectedTab[1]))
    command = command.replace("%filename%",os.path.basename(selectedTab[1]))
    command = command.replace("%selection%",selectedTab[0].selectedText())
    if terminal:
        if platform.system() == 'Windows':
            subprocess.call(["cmd.exe","/C",command])
            pass
        elif platform.system() == 'Darwin':
            #subprocess.call(('open', filepath))
            pass
        else:
            subprocess.call(["x-terminal-emulator","-e",command])
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

def getDataPath():
    if os.getenv("JDTEXTEDIT_DATA_PATH"):
        return os.getenv("JDTEXTEDIT_DATA_PATH")
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
