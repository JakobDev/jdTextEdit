from PyQt5.QtWidgets import QWidget, QComboBox, QCheckBox, QLabel, QHBoxLayout, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase

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

    def updateTab(self, settings):
        self.positionComboBox.setCurrentIndex(settings.tabBarPosition)
        self.hideTabBarCheckBox.setChecked(settings.hideTabBar)
        self.lastTabCheckBox.setChecked(settings.exitLastTab)
        self.closeButtonCheckBox.setChecked(settings.closeButtonTab)
        self.allowTabMoveCheckBox.setChecked(settings.allowTabMove)
        self.tabDoubleClickCloseCheckBox.setChecked(settings.tabDoubleClickClose)

    def getSettings(self, settings):
        settings.tabBarPosition = self.positionComboBox.currentIndex()
        settings.hideTabBar = bool(self.hideTabBarCheckBox.checkState())
        settings.exitLastTab = bool(self.lastTabCheckBox.checkState())
        settings.closeButtonTab = bool(self.closeButtonCheckBox.checkState())
        settings.allowTabMove = bool(self.allowTabMoveCheckBox.checkState())
        settings.tabDoubleClickClose = bool(self.tabDoubleClickCloseCheckBox.checkState())

    def title(self):
        return self.env.translate("settingsWindow.tabBar")
