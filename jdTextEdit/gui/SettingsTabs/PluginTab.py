from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView, QAbstractItemView
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.Settings import Settings
from PyQt6.QtCore import Qt

class PluginTab(QTableWidget,SettingsTabBase):
    def __init__(self, env):
        super().__init__(0,4)
        self.env = env

        self.setHorizontalHeaderLabels((
            env.translate("settingsWindow.plugins.header.enabled"),
            env.translate("settingsWindow.plugins.header.name"),
            env.translate("settingsWindow.plugins.header.version"),
            env.translate("settingsWindow.plugins.header.author"),
        ))
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().hide()

    def updateTab(self, settings: Settings):
        for i in range(self.rowCount()):
            if self.pluginID[i] in settings.disabledPlugins:
                self.cellWidget(i,0).setChecked(False)
            else:
                self.cellWidget(i,0).setChecked(True)

    def getSettings(self, settings: Settings):
        settings.disabledPlugins = []
        for i in range(self.rowCount()):
            if not self.cellWidget(i,0).checkState():
                settings.disabledPlugins.append(self.pluginID[i])

    def setup(self):
        count = 0
        self.pluginID = []
        for key, value in self.env.plugins.items():
            nameItem = QTableWidgetItem(value["name"])
            nameItem.setFlags(nameItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            versionItem = QTableWidgetItem(value["version"])
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            authorItem = QTableWidgetItem(value["author"])
            authorItem.setFlags(authorItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.insertRow(count)
            self.setCellWidget(count,0,QCheckBox())
            self.setItem(count,1,nameItem)
            self.setItem(count,2,versionItem)
            self.setItem(count,3,authorItem)
            self.pluginID.append(key)
            count += 1

    def title(self) -> str:
        return self.env.translate("settingsWindow.plugins")
