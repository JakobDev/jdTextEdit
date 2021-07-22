from PyQt6.QtWidgets import QWidget, QRadioButton, QLineEdit, QPushButton, QLabel, QFileDialog, QHBoxLayout, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.Settings import Settings

class PathEditWidget(QWidget):
    def __init__(self,env,typeSetting: str, customPathSetting: str):
        super().__init__()
        self.typeSetting = typeSetting
        self.customPathSetting = customPathSetting

        self.useCurrentFilePath = QRadioButton(env.translate("settingsWindow.paths.radioButton.followCurrentDocument"))
        self.useLatestDirectory = QRadioButton(env.translate("settingsWindow.paths.radioButton.rememberLastDirectory"))
        self.useCustomPath = QRadioButton(env.translate("settingsWindow.paths.radioButton.useCustomDirectory"))
        self.pathEdit = QLineEdit()
        self.browseButton = QPushButton(env.translate("button.browse"))

        self.useCustomPath.toggled.connect(self.updatePathEditEnabled)
        self.browseButton.clicked.connect(self.browseButtonClicked)

        pathLayout = QHBoxLayout()
        pathLayout.addWidget(self.pathEdit)
        pathLayout.addWidget(self.browseButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.useCurrentFilePath)
        mainLayout.addWidget(self.useLatestDirectory)
        mainLayout.addWidget(self.useCustomPath)
        mainLayout.addLayout(pathLayout)

        self.setLayout(mainLayout)

    def updateWidget(self,settings: Settings):
        self.useCurrentFilePath.setChecked(False)
        self.useLatestDirectory.setChecked(False)
        self.useCustomPath.setChecked(False)
        currentTypeSetting = settings.get(self.typeSetting)
        if currentTypeSetting == 0:
            self.useCurrentFilePath.setChecked(True)
        elif currentTypeSetting == 1:
            self.useLatestDirectory.setChecked(True)
        elif currentTypeSetting == 2:
            self.useCustomPath.setChecked(True)
        self.pathEdit.setText(settings.get(self.customPathSetting))
        self.updatePathEditEnabled()

    def getSettings(self,settings: Settings):
        if  self.useCurrentFilePath.isChecked():
            settings.set(self.typeSetting,0)
        elif self.useLatestDirectory.isChecked():
            settings.set(self.typeSetting,1)
        elif self.useCustomPath.isChecked():
            settings.set(self.typeSetting,2)
        settings.set(self.customPathSetting,self.pathEdit.text())

    def updatePathEditEnabled(self):
        enabled = self.useCustomPath.isChecked()
        self.pathEdit.setEnabled(enabled)
        self.browseButton.setEnabled(enabled)

    def browseButtonClicked(self):
        path = QFileDialog.getExistingDirectory(self)
        if path:
            self.pathEdit.setText(path)

class PathsTab(QWidget,SettingsTabBase):
    def __init__(self,env):
        super().__init__()
        self.env = env

        self.saveWidget = PathEditWidget(env,"saveFilePathType","saveFileCustomPath")
        self.openWidget = PathEditWidget(env,"openFilePathType","openFileCustomPath")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel(env.translate("settingsWindow.paths.label.save")))
        mainLayout.addWidget(self.saveWidget)
        mainLayout.addWidget(QLabel(env.translate("settingsWindow.paths.label.open")))
        mainLayout.addWidget(self.openWidget)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def updateTab(self,settings: Settings):
        self.saveWidget.updateWidget(settings)
        self.openWidget.updateWidget(settings)

    def getSettings(self,settings: Settings):
        self.saveWidget.getSettings(settings)
        self.openWidget.getSettings(settings)

    def title(self) -> str:
        return self.env.translate("settingsWindow.paths")
