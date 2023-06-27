from PyQt6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QTextBrowser, QCheckBox, QPushButton, QHBoxLayout, QVBoxLayout, QAbstractItemView, QHeaderView, QMessageBox
from jdTextEdit.Functions import readJsonFile
from typing import TYPE_CHECKING
from PyQt6.QtCore import Qt
import requests
import shutil
import json
import sys
import os


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class PluginManagerWindow(QWidget):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env
        self.setupDone = False
        self.pluginList = []
        self.pluginTable = QTableWidget(0, 4)
        self.descriptionView = QTextBrowser()
        okButton = QPushButton(env.translate("pluginManagerWindow.button.ok"))
        cancelButton = QPushButton(env.translate("pluginManagerWindow.button.cancel"))

        self.pluginTable.setHorizontalHeaderLabels((
            env.translate("pluginManagerWindow.header.installed"),
            env.translate("pluginManagerWindow.header.name"),
            env.translate("pluginManagerWindow.header.version"),
            env.translate("pluginManagerWindow.header.author"),
        ))
        self.pluginTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.pluginTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.pluginTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.pluginTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.pluginTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.pluginTable.verticalHeader().hide()
        self.pluginTable.currentCellChanged.connect(lambda row: self.descriptionView.setHtml(self.pluginList[row]["description"]))

        okButton.clicked.connect(self.doChanges)
        cancelButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        if env.settings.get("swapOkCancel"):
            buttonLayout.addWidget(okButton)
            buttonLayout.addWidget(cancelButton)
        else:
            buttonLayout.addWidget(cancelButton)
            buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.pluginTable)
        mainLayout.addWidget(self.descriptionView)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.resize(650, 550)
        self.setWindowTitle(env.translate("pluginManagerWindow.title"))

    def openWindow(self) -> None:
        if not self.setupDone:
            if not self.setupPluginList():
                return

            self.installedList = readJsonFile(os.path.join(self.env.dataDir, "installedPlugins.json"), {})
            self.setupDone = True
        for i in range(self.pluginTable.rowCount()):
            if self.pluginList[i]["id"] in self.installedList:
                self.pluginTable.cellWidget(i, 0).setChecked(True)
            else:
                self.pluginTable.cellWidget(i, 0).setChecked(False)
        self.show()
        self.pluginTable.setCurrentCell(-1,-1)
        self.descriptionView.setHtml(self.env.translate("pluginManagerWindow.welcomeMessage").replace("{{link}}", "<a href=\"https://codeberg.org/JakobDev/jdTextEdit-Plugins\">https://codeberg.org/JakobDev/jdTextEdit-Plugins</a> "))

    def setupPluginList(self):
        try:
            data = requests.get("https://codeberg.org/JakobDev/jdTextEdit-Plugins/raw/branch/master/Plugins.json").json()
        except requests.exceptions.RequestException:
            QMessageBox.critical(self, self.env.translate("pluginManagerWindow.messageBox.noInternet.title"), self.env.translate("pluginManagerWindow.messageBox.noInternet.text").replace("{{url}}", "https://codeberg.org/JakobDev/jdTextEdit-Plugins/raw/branch/master/Plugins.json"))
            return False

        except Exception as e:
            QMessageBox.critical(self, self.env.translate("pluginManagerWindow.messageBox.error.title"), str(e))
            return False

        for count, i in enumerate(data["pluginlist"]):
            nameItem = QTableWidgetItem(i["name"])
            nameItem.setFlags(nameItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            versionItem = QTableWidgetItem(i["version"])
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            authorItem = QTableWidgetItem(i["author"])
            authorItem.setFlags(authorItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.pluginTable.insertRow(count)
            self.pluginTable.setCellWidget(count,0,QCheckBox())
            self.pluginTable.setItem(count, 1, nameItem)
            self.pluginTable.setItem(count, 2, versionItem)
            self.pluginTable.setItem(count, 3, authorItem)
            self.pluginList.append({"id": i["id"], "description": i["description"], "files": i["files"], "neededVersion": i["neededVersion"]})

        return True

    def installPlugin(self, index: int) -> bool:
        if float(self.pluginList[index]["neededVersion"]) > float(self.env.version):
            QMessageBox.critical(self, self.env.translate("pluginManagerWindow.messageBox.outdatedVersion.title"), self.env.translate("pluginManagerWindow.messageBox.outdatedVersion.text"))
            return False

        installPath = os.path.join(self.env.dataDir, "plugins", self.pluginList[index]["id"])
        for filename, url in self.pluginList[index]["files"].items():
            try:
                r = requests.get(url)
                try:
                    os.makedirs(os.path.dirname(os.path.join(installPath, filename)))
                except Exception:
                    pass
                f = open(os.path.join(installPath, filename), "w")
                f.write(r.text)
                f.close()
                r.close()
            except Exception as e:
                print(e)
                return False
        self.installedList[self.pluginList[index]["id"]] = True
        return True

    def doChanges(self) -> None:
        for i in range(self.pluginTable.rowCount()):
            if self.pluginTable.cellWidget(i, 0).checkState():
                if not self.pluginList[i]["id"] in self.installedList:
                    self.installPlugin(i)
            else:
                if self.pluginList[i]["id"] in self.installedList:
                    try:
                        shutil.rmtree(os.path.join(self.env.dataDir, "plugins", self.pluginList[i]["id"]))
                        del self.installedList[self.pluginList[i]["id"]]
                    except Exception as e:
                        print(e, file=sys.stderr)

        with open(os.path.join(self.env.dataDir, "installedPlugins.json"), "w", encoding="utf-8") as f:
            json.dump(self.installedList, f, ensure_ascii=False, indent=4)

        self.close()
