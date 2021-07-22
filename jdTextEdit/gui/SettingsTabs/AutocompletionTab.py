from PyQt6.QtWidgets import QWidget, QCheckBox, QSpinBox, QLabel, QVBoxLayout, QHBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.Settings import Settings

class AutocompletionTab(QWidget,SettingsTabBase):
    def __init__(self, env):
        super().__init__()
        self.env = env

        self.enableAutocompletionCheckBox = QCheckBox(env.translate("settingsWindow.autocompletion.checkbox.enableAutocompletion"))
        self.useWordsFromDocument = QCheckBox(env.translate("settingsWindow.autocompletion.checkbox.useWordsFromDocument"))
        self.useAPI = QCheckBox(env.translate("settingsWindow.autocompletion.checkbox.useAPI"))
        self.caseSensitive = QCheckBox(env.translate("settingsWindow.autocompletion.checkbox.caseSensitive"))
        self.replaceWord = QCheckBox(env.translate("settingsWindow.autocompletion.checkbox.replaceWord"))
        self.thresholdLabel = QLabel(env.translate("settingsWindow.autocompletion.label.threshold"))
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
        enabled = bool(self.enableAutocompletionCheckBox.checkState())
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
        settings.set("enableAutocompletion",self.enableAutocompletionCheckBox.isChecked())
        settings.set("autocompletionUseDocument",self.useWordsFromDocument.isChecked())
        settings.set("autocompletionUseAPI",self.useAPI.isChecked())
        settings.set("autocompletionCaseSensitive",self.caseSensitive.isChecked())
        settings.set("autocompletionReplaceWord",self.replaceWord.isChecked())
        settings.set("autocompleteThreshold",self.thresholdSpinBox.value())

    def title(self) -> str:
        return self.env.translate("settingsWindow.autocompletion")
