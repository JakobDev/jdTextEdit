from PyQt5.QtWidgets import QWidget, QCheckBox, QLineEdit, QLabel, QSpinBox, QHBoxLayout, QVBoxLayout

class SaveTab(QWidget):
    def __init__(self, env):
        super().__init__()
        self.eolFileEndCheckBox = QCheckBox(env.translate("settingsWindow.save.checkBox.eolFileEnd"))
        self.stripSpacesCheckBox = QCheckBox(env.translate("settingsWindow.save.checkBox.stripSpaces"))
        self.backupCheckBox = QCheckBox(env.translate("settingsWindow.save.checkBox.enableBackup"))
        self.autoSaveCheckBox = QCheckBox(env.translate("settingsWindow.save.checkBox.enableAutoSave"))
        self.autoSaveIntervalSpinBox = QSpinBox()
        self.backupExtensionEdit = QLineEdit()

        backupExtensionLayout = QHBoxLayout()
        backupExtensionLayout.addWidget(QLabel(env.translate("settingsWindow.save.label.backupExtension")))
        backupExtensionLayout.addStretch()
        backupExtensionLayout.addWidget(self.backupExtensionEdit)

        autoSaveIntervalLayout = QHBoxLayout()
        autoSaveIntervalLayout.addWidget(QLabel(env.translate("settingsWindow.save.label.autoSaveInterval")))
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

    def updateTab(self, settings):
        self.eolFileEndCheckBox.setChecked(settings.eolFileEnd)
        self.stripSpacesCheckBox.setChecked(settings.stripSpacesSave)
        self.backupCheckBox.setChecked(settings.saveBackupEnabled)
        self.backupExtensionEdit.setText(settings.saveBackupExtension)
        self.autoSaveCheckBox.setChecked(settings.enableAutoSave)
        self.autoSaveIntervalSpinBox.setValue(settings.autoSaveInterval)

    def getSettings(self, settings):
        settings.eolFileEnd = bool(self.eolFileEndCheckBox.checkState())
        settings.stripSpacesSave = bool(self.stripSpacesCheckBox.checkState())
        settings.saveBackupEnabled =  bool(self.backupCheckBox.checkState())
        settings.saveBackupExtension = self.backupExtensionEdit.text()
        settings.enableAutoSave =  bool(self.autoSaveCheckBox.checkState())
        settings.autoSaveInterval = self.autoSaveIntervalSpinBox.value()
        return settings
