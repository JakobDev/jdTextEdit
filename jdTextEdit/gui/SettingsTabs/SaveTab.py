from PyQt5.QtWidgets import QWidget, QCheckBox, QLineEdit, QLabel, QSpinBox, QHBoxLayout, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase

class SaveTab(QWidget,SettingsTabBase):
    def __init__(self, env):
        super().__init__()
        self.env = env

        self.eolFileEndCheckBox = QCheckBox(env.translate("settingsWindow.save.checkBox.eolFileEnd"))
        self.stripSpacesCheckBox = QCheckBox(env.translate("settingsWindow.save.checkBox.stripSpaces"))
        self.backupCheckBox = QCheckBox(env.translate("settingsWindow.save.checkBox.enableBackup"))
        self.autoSaveCheckBox = QCheckBox(env.translate("settingsWindow.save.checkBox.enableAutoSave"))
        self.autoSaveLabel = QLabel(env.translate("settingsWindow.save.label.autoSaveInterval"))
        self.backupLabel = QLabel(env.translate("settingsWindow.save.label.backupExtension"))
        self.autoSaveIntervalSpinBox = QSpinBox()
        self.backupExtensionEdit = QLineEdit()

        self.backupCheckBox.stateChanged.connect(self.updateBackupExtensionEnabled)
        self.autoSaveCheckBox.stateChanged.connect(self.updateAutoSaveEnabled)

        backupExtensionLayout = QHBoxLayout()
        backupExtensionLayout.addWidget(self.backupLabel)
        backupExtensionLayout.addStretch()
        backupExtensionLayout.addWidget(self.backupExtensionEdit)

        autoSaveIntervalLayout = QHBoxLayout()
        autoSaveIntervalLayout.addWidget(self.autoSaveLabel)
        autoSaveIntervalLayout.addWidget(self.autoSaveIntervalSpinBox)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.eolFileEndCheckBox)
        mainLayout.addWidget(self.stripSpacesCheckBox)
        mainLayout.addWidget(self.backupCheckBox)
        mainLayout.addLayout(backupExtensionLayout)
        mainLayout.addWidget(self.autoSaveCheckBox)
        mainLayout.addLayout(autoSaveIntervalLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def updateBackupExtensionEnabled(self):
        enabled = bool(self.backupCheckBox.checkState())
        self.backupLabel.setEnabled(enabled)
        self.backupExtensionEdit.setEnabled(enabled)

    def updateAutoSaveEnabled(self):
        enabled =  bool(self.autoSaveCheckBox.checkState())
        self.autoSaveLabel.setEnabled(enabled)
        self.autoSaveIntervalSpinBox.setEnabled(enabled)

    def updateTab(self, settings):
        self.eolFileEndCheckBox.setChecked(settings.eolFileEnd)
        self.stripSpacesCheckBox.setChecked(settings.stripSpacesSave)
        self.backupCheckBox.setChecked(settings.saveBackupEnabled)
        self.backupExtensionEdit.setText(settings.saveBackupExtension)
        self.autoSaveCheckBox.setChecked(settings.enableAutoSave)
        self.autoSaveIntervalSpinBox.setValue(settings.autoSaveInterval)
        self.updateBackupExtensionEnabled()
        self.updateAutoSaveEnabled()

    def getSettings(self, settings):
        settings.eolFileEnd = bool(self.eolFileEndCheckBox.checkState())
        settings.stripSpacesSave = bool(self.stripSpacesCheckBox.checkState())
        settings.saveBackupEnabled =  bool(self.backupCheckBox.checkState())
        settings.saveBackupExtension = self.backupExtensionEdit.text()
        settings.enableAutoSave =  bool(self.autoSaveCheckBox.checkState())
        settings.autoSaveInterval = self.autoSaveIntervalSpinBox.value()

    def title(self):
        return self.env.translate("settingsWindow.save")
