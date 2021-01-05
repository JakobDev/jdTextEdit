from PyQt5.QtWidgets import QWidget, QCheckBox, QComboBox, QSpinBox, QLineEdit, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
import enchant

class SpellCheckingTab(QWidget,SettingsTabBase):
    def __init__(self,env):
        super().__init__()
        self.env = env

        self.enableCheckBox = QCheckBox(env.translate("plugin.spellChecker.settingsTab.enableSpellChecking"))
        self.languageComboBox = QComboBox()
        self.minimumWordLengthSpinBox = QSpinBox()
        self.customPwlCheckBox = QCheckBox(env.translate("plugin.spellChecker.settingsTab.enableCustomPwl"))
        self.customPwlEdit = QLineEdit()

        for i in enchant.list_languages():
            self.languageComboBox.addItem(i,i)

        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel(env.translate("plugin.spellChecker.settingsTab.dictonary")),0,0)
        grid_layout.addWidget(self.languageComboBox,0,1)
        grid_layout.addWidget(QLabel(env.translate("plugin.spellChecker.settingsTab.minimumWordLength")),1,0)
        grid_layout.addWidget(self.minimumWordLengthSpinBox)

        pwl_layout = QHBoxLayout()
        pwl_layout.addWidget(QLabel(env.translate("plugin.spellChecker.settingsTab.customPwlPath")))
        pwl_layout.addWidget(self.customPwlEdit)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.enableCheckBox)
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.customPwlCheckBox)
        main_layout.addLayout(pwl_layout)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

    def updateTab(self,settings):
        self.enableCheckBox.setChecked(settings.spellCheckingEnabled)
        pos = self.languageComboBox.findData(settings.spellCheckingLanguage)
        if pos == -1:
            self.languageComboBox.setCurrentIndex(0)
        else:
            self.languageComboBox.setCurrentIndex(pos)
        self.minimumWordLengthSpinBox.setValue(settings.spellCheckingMinimumWordLength)
        self.customPwlCheckBox.setChecked(settings.spellCheckingEnableCustomPwl)
        self.customPwlEdit.setText(settings.spellCheckingCustomPwlPath)

    def getSettings(self,settings):
        settings.spellCheckingEnabled = bool(self.enableCheckBox.checkState())
        settings.spellCheckingLanguage = self.languageComboBox.currentData()
        settings.spellCheckingMinimumWordLength = self.minimumWordLengthSpinBox.value()
        settings.spellCheckingEnableCustomPwl  = bool(self.customPwlCheckBox.checkState())
        settings.spellCheckingCustomPwlPath = self.customPwlEdit.text()

    def title(self):
        return self.env.translate("plugin.spellChecker.settingsTab")
