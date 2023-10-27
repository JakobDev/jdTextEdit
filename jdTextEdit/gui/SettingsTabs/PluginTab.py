from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView, QAbstractItemView
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt6.QtCore import QCoreApplication
from jdTextEdit.Settings import Settings
from typing import cast, TYPE_CHECKING
from PyQt6.QtCore import Qt


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class _COLUMNS:
    ENABLED = 0
    NAME = 1
    VERSION = 2
    AUTHOR = 3


class PluginTab(QTableWidget, SettingsTabBase):
    def __init__(self, env: "Environment") -> None:
        super().__init__(0, 4)
        self._env = env

        self.setHorizontalHeaderLabels((
            QCoreApplication.translate("PluginTab", "Enabled"),
            QCoreApplication.translate("PluginTab", "Name"),
            QCoreApplication.translate("PluginTab", "Version"),
            QCoreApplication.translate("PluginTab", "Author"),
        ))

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.horizontalHeader().setSectionResizeMode(_COLUMNS.ENABLED, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(_COLUMNS.NAME, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(_COLUMNS.VERSION, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(_COLUMNS.AUTHOR, QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().hide()

    def updateTab(self, settings: Settings) -> None:
        for i in range(self.rowCount()):
            if self.pluginID[i] in settings.disabledPlugins:
                cast(QCheckBox, self.cellWidget(i, _COLUMNS.ENABLED)).setChecked(False)
            else:
                cast(QCheckBox, self.cellWidget(i, _COLUMNS.ENABLED)).setChecked(True)

    def getSettings(self, settings: Settings) -> None:
        disabledPlugins: list[str] = []
        for i in range(self.rowCount()):
            if not cast(QCheckBox, self.cellWidget(i, _COLUMNS.ENABLED)).isChecked():
                self._env.logger.verboseDebug(f"Disable Plugin {self.pluginID[i]}")
                disabledPlugins.append(self.pluginID[i])
        settings.set("disabledPlugins", disabledPlugins)

    def setup(self) -> None:
        count = 0
        self.pluginID: list[str] = []
        for key, value in self._env.plugins.items():
            self.insertRow(count)
            self.setCellWidget(count, _COLUMNS.ENABLED, QCheckBox())

            nameItem = QTableWidgetItem(value["name"])
            nameItem.setFlags(nameItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.setItem(count, _COLUMNS.NAME, nameItem)

            versionItem = QTableWidgetItem(value["version"])
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.setItem(count, _COLUMNS.VERSION, versionItem)

            authorItem = QTableWidgetItem(value["author"])
            authorItem.setFlags(authorItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.setItem(count, _COLUMNS.AUTHOR, authorItem)

            self.pluginID.append(key)
            count += 1

    def title(self) -> str:
        return QCoreApplication.translate("PluginTab", "Plugins")
