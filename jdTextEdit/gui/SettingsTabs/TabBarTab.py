from PyQt6.QtWidgets import QWidget, QComboBox, QCheckBox, QLabel, QHBoxLayout, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt6.QtCore import QCoreApplication
from jdTextEdit.Settings import Settings
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class TabBarTab(QWidget, SettingsTabBase):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env

        self.positionComboBox = QComboBox()
        self.hideTabBarCheckBox = QCheckBox(QCoreApplication.translate("TabBarTab", "Hide Tabbar when only 1 tab is open"))
        self.lastTabCheckBox = QCheckBox(QCoreApplication.translate("TabBarTab", "Exit jdTextEdit when the last tab is closed"))
        self.closeButtonCheckBox = QCheckBox(QCoreApplication.translate("TabBarTab", "Show close button on each tab"))
        self.allowTabMoveCheckBox = QCheckBox(QCoreApplication.translate("TabBarTab", "Allow moving tabs with the mouse"))
        self.tabDoubleClickCloseCheckBox = QCheckBox(QCoreApplication.translate("TabBarTab", "Close tabs with double click"))

        self.positionComboBox.addItem(QCoreApplication.translate("TabBarTab", "Up"))
        self.positionComboBox.addItem(QCoreApplication.translate("TabBarTab", "Bottom"))
        self.positionComboBox.addItem(QCoreApplication.translate("TabBarTab", "Left"))
        self.positionComboBox.addItem(QCoreApplication.translate("TabBarTab", "Right"))

        positionLayout = QHBoxLayout()
        positionLayout.addWidget(QLabel(QCoreApplication.translate("TabBarTab", "Position:")))
        positionLayout.addWidget(self.positionComboBox)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(positionLayout)
        mainLayout.addWidget(self.hideTabBarCheckBox)
        mainLayout.addWidget(self.lastTabCheckBox)
        mainLayout.addWidget(self.closeButtonCheckBox)
        mainLayout.addWidget(self.allowTabMoveCheckBox)
        mainLayout.addWidget(self.tabDoubleClickCloseCheckBox)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def updateTab(self, settings: Settings) -> None:
        self.positionComboBox.setCurrentIndex(settings.tabBarPosition)
        self.hideTabBarCheckBox.setChecked(settings.hideTabBar)
        self.lastTabCheckBox.setChecked(settings.exitLastTab)
        self.closeButtonCheckBox.setChecked(settings.closeButtonTab)
        self.allowTabMoveCheckBox.setChecked(settings.allowTabMove)
        self.tabDoubleClickCloseCheckBox.setChecked(settings.tabDoubleClickClose)

    def getSettings(self, settings: Settings) -> None:
        settings.set("tabBarPosition", self.positionComboBox.currentIndex())
        settings.set("hideTabBar", self.hideTabBarCheckBox.isChecked())
        settings.set("exitLastTab", self.lastTabCheckBox.isChecked())
        settings.set("closeButtonTab", self.closeButtonCheckBox.isChecked())
        settings.set("allowTabMove", self.allowTabMoveCheckBox.isChecked())
        settings.set("tabDoubleClickClose", self.tabDoubleClickCloseCheckBox.isChecked())

    def title(self) -> str:
        return QCoreApplication.translate("TabBarTab", "Tabbar")
