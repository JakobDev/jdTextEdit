from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton
from jdTextEdit.gui.SettingsTabs.GeneralTab import GeneralTab
from jdTextEdit.gui.SettingsTabs.EditorTab import EditorTab
from jdTextEdit.gui.SettingsTabs.AutocompletionTab import AutocompletionTab
from jdTextEdit.gui.SettingsTabs.StyleTab import StyleTab
from jdTextEdit.gui.SettingsTabs.OpenTab import OpenTab
from jdTextEdit.gui.SettingsTabs.SaveTab import SaveTab
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
        self.newTab(GeneralTab,env.translate("settingsWindow.general"))
        self.newTab(EditorTab,env.translate("settingsWindow.editor"))
        self.newTab(AutocompletionTab,env.translate("settingsWindow.autocompletion"))
        self.newTab(StyleTab,env.translate("settingsWindow.style"))
        self.newTab(OpenTab,env.translate("settingsWindow.open"))
        self.newTab(SaveTab,env.translate("settingsWindow.save"))
        self.newTab(ContextMenuTab,env.translate("settingsWindow.contextMenu"))
        self.newTab(ToolbarTab,env.translate("settingsWindow.toolbar"))
        self.newTab(ShortcutTab,env.translate("settingsWindow.shortcuts"))
        if env.settings.loadPlugins:
            self.newTab(PluginTab,env.translate("settingsWindow.plugins"))

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

    def newTab(self, win, title):
        self.tabs.append(win(self.env))
        self.tabWidget.addTab(self.tabs[-1],title)

    def openWindow(self):
        for i in self.tabs:
            i.updateTab(self.env.settings)
        self.show()
        QApplication.setActiveWindow(self)

    def okButtonClicked(self):
        for i in self.tabs:
            self.env.settings = i.getSettings(self.env.settings)
        self.env.mainWindow.updateSettings(self.env.settings)
        for i in range(self.env.mainWindow.tabWidget.count()):
            self.env.mainWindow.tabWidget.widget(i).getCodeEditWidget().setSettings(self.env.settings)
        #self.env.settings.save(os.path.join(self.env.dataDir,"settings.json"))
        self.close()

    def defaultButtonClicked(self):
        defaultSettings = Settings()
        for i in self.tabs:
            i.updateTab(defaultSettings)

    def setup(self):
        for i in self.tabs:
            if hasattr(i,"setup"):
                i.setup()
