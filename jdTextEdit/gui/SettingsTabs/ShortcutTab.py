from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QScrollArea, QKeySequenceEdit, QGridLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.Settings import Settings

class ClearResetButton(QPushButton):
    def __init__(self, text, keySequenceEdit, defaultKeySequence):
        super().__init__(text)
        self.keySequenceEdit = keySequenceEdit
        self.defaultKeySequence = defaultKeySequence
        self.clicked.connect(lambda: self.keySequenceEdit.setKeySequence(self.defaultKeySequence))

class ShortcutTab(QScrollArea,SettingsTabBase):
    def __init__(self, env):
        super().__init__()
        self.env = env

    def updateTab(self, settings):
        for i in self.shortcutList:
            if i[0] in settings.shortcut:
                i[1].setKeySequence(settings.shortcut[i[0]])
            else:
                i[1].setKeySequence("")

    def getSettings(self, settings):
        for i in self.shortcutList:
            if not i[1].keySequence().isEmpty():
                settings.shortcut[i[0]] = i[1].keySequence().toString()
            elif i[0] in settings.shortcut:
                del settings.shortcut[i[0]]

    def setup(self):
        self.shortcutList = []
        mainLayout = QGridLayout()
        self.scrollWidget = QWidget()
        defaultSettings = Settings()
        clearString = self.env.translate("settingsWindow.shortcuts.button.clear")
        resetString = self.env.translate("settingsWindow.shortcuts.button.reset")
        count = 0
        for key, value in self.env.menuActions.items():
            if key == "separator":
                continue
            if value.text().startswith("&"):
                mainLayout.addWidget(QLabel(value.text()[1:]),count,0)
            else:
                mainLayout.addWidget(QLabel(value.text()),count,0)
            keySequenceEdit = QKeySequenceEdit()
            mainLayout.addWidget(keySequenceEdit,count,1)
            self.shortcutList.append([key,keySequenceEdit])
            mainLayout.addWidget(ClearResetButton(clearString,keySequenceEdit,""),count,2)
            if key in defaultSettings.shortcut:
                mainLayout.addWidget(ClearResetButton(resetString,keySequenceEdit,defaultSettings.shortcut[key]),count,3)
            else:
                mainLayout.addWidget(ClearResetButton(resetString,keySequenceEdit,""),count,3)
            count += 1
        self.scrollWidget.setLayout(mainLayout)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

    def title(self):
        return self.env.translate("settingsWindow.shortcuts")
