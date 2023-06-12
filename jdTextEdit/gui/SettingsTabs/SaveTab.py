from PyQt6.QtWidgets import QWidget, QCheckBox, QLineEdit, QLabel, QSpinBox, QHBoxLayout, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.Settings import Settings
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class SaveTab(QWidget, SettingsTabBase):
    def __init__(self, env: "Environment"):
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
        enabled = self.backupCheckBox.isChecked()
        self.backupLabel.setEnabled(enabled)
        self.backupExtensionEdit.setEnabled(enabled)

    def updateAutoSaveEnabled(self):
        enabled = self.autoSaveCheckBox.isChecked()
        self.autoSaveLabel.setEnabled(enabled)
        self.autoSaveIntervalSpinBox.setEnabled(enabled)

    def updateTab(self, settings: Settings) -> None:
        self.eolFileEndCheckBox.setChecked(settings.get("eolFileEnd"))
        self.stripSpacesCheckBox.setChecked(settings.get("stripSpacesSave"))
        self.backupCheckBox.setChecked(settings.get("saveBackupEnabled"))
        self.backupExtensionEdit.setText(settings.get("saveBackupExtension"))
        self.autoSaveCheckBox.setChecked(settings.get("enableAutoSave"))
        self.autoSaveIntervalSpinBox.setValue(settings.get("autoSaveInterval"))
        self.updateBackupExtensionEnabled()
        self.updateAutoSaveEnabled()

    def getSettings(self, settings: Settings) -> None:
        settings.set("eolFileEnd", self.eolFileEndCheckBox.isChecked())
        settings.set("stripSpacesSave", self.stripSpacesCheckBox.isChecked())
        settings.set("saveBackupEnabled", self.backupCheckBox.isChecked())
        settings.set("saveBackupExtension", self.backupExtensionEdit.text())
        settings.set("enableAutoSave", self.autoSaveCheckBox.isChecked())
        settings.set("autoSaveInterval", self.autoSaveIntervalSpinBox.value())

    def title(self) -> str:
        return self.env.translate("settingsWindow.save")
