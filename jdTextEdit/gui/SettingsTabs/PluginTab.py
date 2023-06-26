from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView, QAbstractItemView
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt6.QtCore import QCoreApplication
from jdTextEdit.Settings import Settings
from typing import TYPE_CHECKING
from PyQt6.QtCore import Qt


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class PluginTab(QTableWidget, SettingsTabBase):
    def __init__(self, env: "Environment") -> None:
        super().__init__(0, 4)
        self.env = env

        self.setHorizontalHeaderLabels((
            QCoreApplication.translate("PluginTab", "Enabled"),
            QCoreApplication.translate("PluginTab", "Name"),
            QCoreApplication.translate("PluginTab", "Version"),
            QCoreApplication.translate("PluginTab", "Author"),
        ))

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().hide()

    def updateTab(self, settings: Settings) -> None:
        for i in range(self.rowCount()):
            if self.pluginID[i] in settings.disabledPlugins:
                self.cellWidget(i, 0).setChecked(False)
            else:
                self.cellWidget(i, 0).setChecked(True)

    def getSettings(self, settings: Settings) -> None:
        disabledPlugins: list[str] = []
        for i in range(self.rowCount()):
            if not self.cellWidget(i, 0).checkState():
                disabledPlugins.append(self.pluginID[i])
        settings.set("disabledPlugins", disabledPlugins)

    def setup(self) -> None:
        count = 0
        self.pluginID: list[str] = []
        for key, value in self.env.plugins.items():
            nameItem = QTableWidgetItem(value["name"])
            nameItem.setFlags(nameItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            versionItem = QTableWidgetItem(value["version"])
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            authorItem = QTableWidgetItem(value["author"])
            authorItem.setFlags(authorItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.insertRow(count)
            self.setCellWidget(count, 0, QCheckBox())
            self.setItem(count, 1, nameItem)
            self.setItem(count, 2, versionItem)
            self.setItem(count, 3, authorItem)
            self.pluginID.append(key)
            count += 1

    def title(self) -> str:
        return QCoreApplication.translate("PluginTab", "Plugins")
