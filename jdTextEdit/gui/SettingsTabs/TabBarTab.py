from PyQt6.QtWidgets import QWidget, QComboBox, QCheckBox, QLabel, QHBoxLayout, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.Settings import Settings

class TabBarTab(QWidget,SettingsTabBase):
    def __init__(self, env):
        super().__init__()
        self.env = env

        self.positionComboBox = QComboBox()
        self.hideTabBarCheckBox = QCheckBox(env.translate("settingsWindow.tabBar.checkBox.hideTabBar"))
        self.lastTabCheckBox = QCheckBox(env.translate("settingsWindow.tabBar.checkBox.exitLastTab"))
        self.closeButtonCheckBox = QCheckBox(env.translate("settingsWindow.tabBar.checkBox.closeButton"))
        self.allowTabMoveCheckBox = QCheckBox(env.translate("settingsWindow.tabBar.checkBox.allowTabMove"))
        self.tabDoubleClickCloseCheckBox = QCheckBox(env.translate("settingsWindow.tabBar.checkBox.tabDoubleClickClose"))

        self.positionComboBox.addItem(env.translate("position.up"))
        self.positionComboBox.addItem(env.translate("position.bottom"))
        self.positionComboBox.addItem(env.translate("position.left"))
        self.positionComboBox.addItem(env.translate("position.right"))

        positionLayout = QHBoxLayout()
        positionLayout.addWidget(QLabel(env.translate("settingsWindow.tabBar.label.position")))
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

    def updateTab(self, settings: Settings):
        self.positionComboBox.setCurrentIndex(settings.tabBarPosition)
        self.hideTabBarCheckBox.setChecked(settings.hideTabBar)
        self.lastTabCheckBox.setChecked(settings.exitLastTab)
        self.closeButtonCheckBox.setChecked(settings.closeButtonTab)
        self.allowTabMoveCheckBox.setChecked(settings.allowTabMove)
        self.tabDoubleClickCloseCheckBox.setChecked(settings.tabDoubleClickClose)

    def getSettings(self, settings: Settings):
        settings.set("tabBarPosition",self.positionComboBox.currentIndex())
        settings.set("hideTabBar",self.hideTabBarCheckBox.isChecked())
        settings.set("exitLastTab",self.lastTabCheckBox.isChecked())
        settings.set("closeButtonTab",self.closeButtonCheckBox.isChecked())
        settings.set("allowTabMove",self.allowTabMoveCheckBox.isChecked())
        settings.set("tabDoubleClickClose",self.tabDoubleClickCloseCheckBox.isChecked())

    def title(self) -> str:
        return self.env.translate("settingsWindow.tabBar")
