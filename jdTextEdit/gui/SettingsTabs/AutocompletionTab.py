from PyQt5.QtWidgets import QWidget, QCheckBox, QSpinBox, QLabel, QVBoxLayout, QHBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase

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

    def updateTab(self, settings):
        self.enableAutocompletionCheckBox.setChecked(settings.enableAutocompletion)
        self.useWordsFromDocument.setChecked(settings.autocompletionUseDocument)
        self.useAPI.setChecked(settings.autocompletionUseAPI)
        self.caseSensitive.setChecked(settings.autocompletionCaseSensitive)
        self.replaceWord.setChecked(settings.autocompletionReplaceWord)
        self.thresholdSpinBox.setValue(settings.autocompleteThreshold)
        self.updateSettingsEnabled()

    def getSettings(self, settings):
        settings.enableAutocompletion = bool(self.enableAutocompletionCheckBox.checkState())
        settings.autocompletionUseDocument = bool(self.useWordsFromDocument.checkState())
        settings.autocompletionUseAPI = bool(self.useAPI.checkState())
        settings.autocompletionCaseSensitive = bool(self.caseSensitive.checkState())
        settings.autocompletionReplaceWord = bool(self.replaceWord.checkState())
        settings.autocompleteThreshold = self.thresholdSpinBox.value()

    def title(self):
        return self.env.translate("settingsWindow.autocompletion")
