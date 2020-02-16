from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QTextBrowser, QCheckBox, QPushButton, QHBoxLayout, QVBoxLayout, QAbstractItemView, QHeaderView
from jdTextEdit.Functions import showMessageBox, readJsonFile
from PyQt5.QtCore import Qt
import requests
import shutil
import json
import os

class PluginManagerWindow(QWidget):
    def __init__(self, env):
        super().__init__()
        self.env = env
        self.setupDone = False
        self.pluginList = []
        self.pluginTable = QTableWidget(0,4)
        self.descriptionView = QTextBrowser()
        okButton = QPushButton(env.translate("button.ok"))
        cancelButton = QPushButton(env.translate("button.cancel"))

        self.pluginTable.setHorizontalHeaderLabels((
            env.translate("pluginManagerWindow.header.installed"),
            env.translate("pluginManagerWindow.header.name"),
            env.translate("pluginManagerWindow.header.version"),
            env.translate("pluginManagerWindow.header.author"),
        ))
        self.pluginTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pluginTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.pluginTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.pluginTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.pluginTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.pluginTable.verticalHeader().hide()
        self.pluginTable.currentCellChanged.connect(lambda row: self.descriptionView.setHtml(self.pluginList[row]["description"]))

        okButton.clicked.connect(self.doChanges)
        cancelButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.pluginTable)
        mainLayout.addWidget(self.descriptionView)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.resize(650, 550)
        self.setWindowTitle(env.translate("pluginManagerWindow.title"))

    def openWindow(self):
        if not self.setupDone:
            if not self.setupPluginList():
                return
            self.installedList = readJsonFile(os.path.join(self.env.dataDir,"installedPlugins.json"),{})
            self.setupDone = True
        for i in range(self.pluginTable.rowCount()):
            if self.pluginList[i]["id"] in self.installedList:
                self.pluginTable.cellWidget(i,0).setChecked(True)
            else:
                self.pluginTable.cellWidget(i,0).setChecked(False)
        self.show()
        self.pluginTable.setCurrentCell(-1,-1)
        self.descriptionView.setHtml(self.env.translate("pluginManagerWindow.welcomeMessage"))

    def setupPluginList(self):
        try:
            data = requests.get("https://gitlab.com/JakobDev/jdTextEdit-Plugins/raw/master/Plugins.json").json()
        except requests.exceptions.RequestException:
            showMessageBox(self.env.translate("pluginManagerWindow.messageBox.noInternet.title"),self.env.translate("pluginManagerWindow.messageBox.noInternet.text"))
            return False
        except Exception as e:
            showMessageBox(self.env.translate("pluginManagerWindow.messageBox.error.title"),str(e))
            return False
        for count, i in enumerate(data["pluginlist"]):
            nameItem = QTableWidgetItem(i["name"])
            nameItem.setFlags(nameItem.flags() ^ Qt.ItemIsEditable)
            versionItem = QTableWidgetItem(i["version"])
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemIsEditable)
            authorItem = QTableWidgetItem(i["author"])
            authorItem.setFlags(authorItem.flags() ^ Qt.ItemIsEditable)
            self.pluginTable.insertRow(count)
            self.pluginTable.setCellWidget(count,0,QCheckBox())
            self.pluginTable.setItem(count,1,nameItem)
            self.pluginTable.setItem(count,2,versionItem)
            self.pluginTable.setItem(count,3,authorItem)
            self.pluginList.append({"id":i["id"],"description":i["description"],"files":i["files"],"neededVersion":i["neededVersion"]})
        return True    

    def installPlugin(self, index):
        if float(self.pluginList[index]["neededVersion"]) > float(self.env.version):
            showMessageBox("pluginManagerWindow.messageBox.outdatedVersion.title","pluginManagerWindow.messageBox.outdatedVersion.text")
            return False
        installPath = os.path.join(self.env.dataDir,"plugins",self.pluginList[index]["id"])
        for filename, url in self.pluginList[index]["files"].items():
            try:
                r = requests.get(url)
                try:
                    os.makedirs(os.path.dirname(os.path.join(installPath,filename)))
                except:
                    pass
                f = open(os.path.join(installPath,filename),"w")
                f.write(r.text)
                f.close()
                r.close()
            except Exception as e:
                print(e)
                return False
        self.installedList[self.pluginList[index]["id"]] = True
        return True
         
    def doChanges(self):
        for i in range(self.pluginTable.rowCount()):
            if self.pluginTable.cellWidget(i,0).checkState():
                if not self.pluginList[i]["id"] in self.installedList:
                    self.installPlugin(i)
            else:
                if self.pluginList[i]["id"] in self.installedList:
                    try:
                        shutil.rmtree(os.path.join(self.env.dataDir,"plugins",self.pluginList[i]["id"]))
                        del self.installedList[self.pluginList[i]["id"]]
                    except Exception as e:
                        print(e)
        with open(os.path.join(self.env.dataDir,"installedPlugins.json"), 'w', encoding='utf-8') as f:
            json.dump(self.installedList, f, ensure_ascii=False, indent=4)
        self.close()
