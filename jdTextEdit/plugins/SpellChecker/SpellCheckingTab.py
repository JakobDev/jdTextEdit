from PyQt6.QtWidgets import QWidget, QCheckBox, QComboBox, QSpinBox, QLineEdit, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from typing import TYPE_CHECKING
import enchant


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment
    from jdTextEdit.Settings import Settings


class SpellCheckingTab(QWidget, SettingsTabBase):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env

        self.enableCheckBox = QCheckBox(env.translate("plugin.spellChecker.settingsTab.enableSpellChecking"))
        self.dictonaryLabel = QLabel(env.translate("plugin.spellChecker.settingsTab.dictonary"))
        self.languageComboBox = QComboBox()
        self.minimumWordLengthLabel = QLabel(env.translate("plugin.spellChecker.settingsTab.minimumWordLength"))
        self.minimumWordLengthSpinBox = QSpinBox()
        self.customPwlCheckBox = QCheckBox(env.translate("plugin.spellChecker.settingsTab.enableCustomPwl"))
        self.customPwlEdit = QLineEdit()
        self.customPwlLabel = QLabel(env.translate("plugin.spellChecker.settingsTab.customPwlPath"))

        for i in enchant.list_languages():
            self.languageComboBox.addItem(i,i)

        self.enableCheckBox.stateChanged.connect(self.updateSettingsEnabled)
        self.customPwlCheckBox.stateChanged.connect(self.updateCustomPwlEnabled)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.dictonaryLabel,0,0)
        grid_layout.addWidget(self.languageComboBox,0,1)
        grid_layout.addWidget(self.minimumWordLengthLabel,1,0)
        grid_layout.addWidget(self.minimumWordLengthSpinBox)

        pwl_layout = QHBoxLayout()
        pwl_layout.addWidget(self.customPwlLabel)
        pwl_layout.addWidget(self.customPwlEdit)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.enableCheckBox)
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.customPwlCheckBox)
        main_layout.addLayout(pwl_layout)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

    def updateSettingsEnabled(self) -> None:
        enabled = self.enableCheckBox.isChecked()
        self.dictonaryLabel.setEnabled(enabled)
        self.languageComboBox.setEnabled(enabled)
        self.minimumWordLengthLabel.setEnabled(enabled)
        self.minimumWordLengthSpinBox.setEnabled(enabled)
        self.customPwlCheckBox.setEnabled(enabled)
        self.updateCustomPwlEnabled()

    def updateCustomPwlEnabled(self):
        enabled = bool(self.enableCheckBox.checkState()) and self.customPwlCheckBox.isChecked()
        self.customPwlEdit.setEnabled(enabled)
        self.customPwlLabel.setEnabled(enabled)

    def updateTab(self, settings: "Settings") -> None:
        self.enableCheckBox.setChecked(settings.spellCheckingEnabled)
        pos = self.languageComboBox.findData(settings.spellCheckingLanguage)
        if pos == -1:
            self.languageComboBox.setCurrentIndex(0)
        else:
            self.languageComboBox.setCurrentIndex(pos)
        self.minimumWordLengthSpinBox.setValue(settings.spellCheckingMinimumWordLength)
        self.customPwlCheckBox.setChecked(settings.spellCheckingEnableCustomPwl)
        self.customPwlEdit.setText(settings.spellCheckingCustomPwlPath)
        self.updateSettingsEnabled()

    def getSettings(self, settings: "Settings") -> None:
        settings.set("spellCheckingEnabled", self.enableCheckBox.isChecked())
        settings.set("spellCheckingLanguage", self.languageComboBox.currentData())
        settings.set("spellCheckingMinimumWordLength", self.minimumWordLengthSpinBox.value())
        settings.set("spellCheckingEnableCustomPwl", self.customPwlCheckBox.isChecked())
        settings.set("spellCheckingCustomPwlPath", self.customPwlEdit.text())

    def title(self) -> str:
        return self.env.translate("plugin.spellChecker.settingsTab")
