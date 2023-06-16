from PyQt6.QtWidgets import QWidget, QCheckBox, QSpinBox, QLabel, QVBoxLayout, QHBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt6.QtCore import QCoreApplication
from jdTextEdit.Settings import Settings
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class AutocompletionTab(QWidget, SettingsTabBase):
    def __init__(self, env: "Environment"):
        super().__init__()
        self.env = env

        self.enableAutocompletionCheckBox = QCheckBox(QCoreApplication.translate("AutocompletionTab", "Enable Autocompletion"))
        self.useWordsFromDocument = QCheckBox(QCoreApplication.translate("AutocompletionTab", "Use Words from Document"))
        self.useAPI = QCheckBox(QCoreApplication.translate("AutocompletionTab", "Use API"))
        self.caseSensitive = QCheckBox(QCoreApplication.translate("AutocompletionTab", "Case Sensitive"))
        self.replaceWord = QCheckBox(QCoreApplication.translate("AutocompletionTab", "Replace Word"))
        self.thresholdLabel = QLabel(QCoreApplication.translate("AutocompletionTab", "Autocomplete at this char:"))
        self.thresholdSpinBox = QSpinBox()

        self.enableAutocompletionCheckBox.stateChanged.connect(self.updateSettingsEnabled)

        thresholdLayout = QHBoxLayout()
        thresholdLayout.addWidget(self.thresholdLabel)
        thresholdLayout.addWidget(self.thresholdSpinBox)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.enableAutocompletionCheckBox)
        mainLayout.addWidget(self.useWordsFromDocument)
        mainLayout.addWidget(self.useAPI)
        mainLayout.addWidget(self.caseSensitive)
        mainLayout.addWidget(self.replaceWord)
        mainLayout.addLayout(thresholdLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def updateSettingsEnabled(self):
        enabled = self.enableAutocompletionCheckBox.isChecked()
        self.useWordsFromDocument.setEnabled(enabled)
        self.useAPI.setEnabled(enabled)
        self.caseSensitive.setEnabled(enabled)
        self.replaceWord.setEnabled(enabled)
        self.thresholdLabel.setEnabled(enabled)
        self.thresholdSpinBox.setEnabled(enabled)

    def updateTab(self, settings: Settings):
        self.enableAutocompletionCheckBox.setChecked(settings.enableAutocompletion)
        self.useWordsFromDocument.setChecked(settings.autocompletionUseDocument)
        self.useAPI.setChecked(settings.autocompletionUseAPI)
        self.caseSensitive.setChecked(settings.autocompletionCaseSensitive)
        self.replaceWord.setChecked(settings.autocompletionReplaceWord)
        self.thresholdSpinBox.setValue(settings.autocompleteThreshold)
        self.updateSettingsEnabled()

    def getSettings(self, settings: Settings):
        settings.set("enableAutocompletion", self.enableAutocompletionCheckBox.isChecked())
        settings.set("autocompletionUseDocument", self.useWordsFromDocument.isChecked())
        settings.set("autocompletionUseAPI", self.useAPI.isChecked())
        settings.set("autocompletionCaseSensitive", self.caseSensitive.isChecked())
        settings.set("autocompletionReplaceWord", self.replaceWord.isChecked())
        settings.set("autocompleteThreshold", self.thresholdSpinBox.value())

    def title(self) -> str:
        return QCoreApplication.translate("AutocompletionTab", "Autocompletion")
