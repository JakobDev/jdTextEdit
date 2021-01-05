from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton
from jdTextEdit.gui.SettingsTabs.GeneralTab import GeneralTab
from jdTextEdit.gui.SettingsTabs.EditorTab import EditorTab
from jdTextEdit.gui.SettingsTabs.AutocompletionTab import AutocompletionTab
from jdTextEdit.gui.SettingsTabs.StyleTab import StyleTab
from jdTextEdit.gui.SettingsTabs.TabBarTab import TabBarTab
from jdTextEdit.gui.SettingsTabs.OpenTab import OpenTab
from jdTextEdit.gui.SettingsTabs.SaveTab import SaveTab
from jdTextEdit.gui.SettingsTabs.BigFilesTab import BigFilesTab
from jdTextEdit.gui.SettingsTabs.EditorconfigTab import EditorconfigTab
from jdTextEdit.gui.SettingsTabs.ContextMenuTab import ContextMenuTab
from jdTextEdit.gui.SettingsTabs.ToolbarTab import ToolbarTab
from jdTextEdit.gui.SettingsTabs.ShortcutTab import ShortcutTab
from jdTextEdit.gui.SettingsTabs.PluginTab import PluginTab
from jdTextEdit.Functions import restoreWindowState
from jdTextEdit.Settings import Settings
import os

class SettingsWindow(QWidget):
    def __init__(self,env):
        super().__init__()
        self.env = env
        self.tabWidget = QTabWidget()
        self.tabs = []
        #self.newTab(GeneralTab(env))
        #self.newTab(EditorTab(env))
        #self.newTab(AutocompletionTab(env))
        #self.newTab(StyleTab(self.env))
        #self.newTab(TabBarTab(env))
        #self.newTab(OpenTab(env))
        #self.newTab(SaveTab(env))
        #self.newTab(BigFilesTab(env))
        #self.newTab(EditorconfigTab(env))
        #self.newTab(ContextMenuTab(env))
        #self.newTab(ToolbarTab(env))
        #self.newTab(ShortcutTab(env))
        #if env.settings.loadPlugins:
           #self.newTab(PluginTab(env))

        okButton = QPushButton(env.translate("button.ok"))
        cancelButton = QPushButton(env.translate("button.cancel"))
        defaultButton = QPushButton(env.translate("settingsWindow.button.default"))

        okButton.clicked.connect(self.okButtonClicked)
        cancelButton.clicked.connect(self.close)
        defaultButton.clicked.connect(self.defaultButtonClicked)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(defaultButton)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(okButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(env.translate("settingsWindow.title"))
        restoreWindowState(self,env.windowState,"SettingsWindow")

    def newTab(self,tab):
        self.tabs.append(tab)
        self.tabWidget.addTab(tab,tab.title())

    def openWindow(self):
        for i in self.tabs:
            i.updateTab(self.env.settings)
        self.show()
        QApplication.setActiveWindow(self)

    def okButtonClicked(self):
        for i in self.tabs:
            i.getSettings(self.env.settings)
        self.env.mainWindow.updateSettings(self.env.settings)
        self.env.applicationSignals.settingsChanged.emit(self.env.settings)
        for i in range(self.env.mainWindow.tabWidget.count()):
            self.env.mainWindow.tabWidget.widget(i).getCodeEditWidget().setSettings(self.env.settings)
        self.close()

    def defaultButtonClicked(self):
        defaultSettings = Settings(defaultSettings=self.env.defaultSettings)
        for i in self.tabs:
            i.updateTab(defaultSettings)

    def setup(self):
        self.newTab(GeneralTab(self.env))
        self.newTab(EditorTab(self.env))
        self.newTab(AutocompletionTab(self.env))
        self.newTab(StyleTab(self.env))
        self.newTab(TabBarTab(self.env))
        self.newTab(OpenTab(self.env))
        self.newTab(SaveTab(self.env))
        self.newTab(BigFilesTab(self.env))
        self.newTab(EditorconfigTab(self.env))
        self.newTab(ContextMenuTab(self.env))
        self.newTab(ToolbarTab(self.env))
        self.newTab(ShortcutTab(self.env))
        for i in self.env.customSettingsTabs:
            self.newTab(i)
        if self.env.settings.loadPlugins:
            self.newTab(PluginTab(self.env))
        for i in self.tabs:
            if hasattr(i,"setup"):
                i.setup()
