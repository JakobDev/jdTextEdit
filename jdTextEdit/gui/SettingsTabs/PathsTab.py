from PyQt6.QtWidgets import QWidget, QGroupBox, QRadioButton, QLineEdit, QPushButton, QLabel, QFileDialog, QHBoxLayout, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt6.QtCore import QCoreApplication
from jdTextEdit.Settings import Settings
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class PathEditWidget(QGroupBox):
    def __init__(self, typeSetting: str, customPathSetting: str) -> None:
        super().__init__()
        self.typeSetting = typeSetting
        self.customPathSetting = customPathSetting

        self.useCurrentFilePath = QRadioButton(QCoreApplication.translate("PathsTab", "Follow current document"))
        self.useLatestDirectory = QRadioButton(QCoreApplication.translate("PathsTab", "Remember last used directory"))
        self.useCustomPath = QRadioButton(QCoreApplication.translate("PathsTab", "Use custom directory"))
        self.pathEdit = QLineEdit()
        self.browseButton = QPushButton(QCoreApplication.translate("PathsTab", "Browse"))

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

    def updateWidget(self, settings: Settings) -> None:
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

    def getSettings(self,settings: Settings) -> None:
        if self.useCurrentFilePath.isChecked():
            settings.set(self.typeSetting, 0)
        elif self.useLatestDirectory.isChecked():
            settings.set(self.typeSetting, 1)
        elif self.useCustomPath.isChecked():
            settings.set(self.typeSetting, 2)

        settings.set(self.customPathSetting, self.pathEdit.text())

    def updatePathEditEnabled(self) -> None:
        enabled = self.useCustomPath.isChecked()
        self.pathEdit.setEnabled(enabled)
        self.browseButton.setEnabled(enabled)

    def browseButtonClicked(self) -> None:
        path = QFileDialog.getExistingDirectory(self)
        if path:
            self.pathEdit.setText(path)


class PathsTab(QWidget, SettingsTabBase):
    def __init__(self, env: "Environment"):
        super().__init__()
        self.env = env

        self.saveWidget = PathEditWidget("saveFilePathType", "saveFileCustomPath")
        self.openWidget = PathEditWidget("openFilePathType", "openFileCustomPath")

        self.saveWidget.setTitle(QCoreApplication.translate("PathsTab", "Save"))
        self.openWidget.setTitle(QCoreApplication.translate("PathsTab", "Open"))

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.saveWidget)
        mainLayout.addWidget(self.openWidget)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def updateTab(self, settings: Settings) -> None:
        self.saveWidget.updateWidget(settings)
        self.openWidget.updateWidget(settings)

    def getSettings(self, settings: Settings) -> None:
        self.saveWidget.getSettings(settings)
        self.openWidget.getSettings(settings)

    def title(self) -> str:
        return QCoreApplication.translate("PathsTab", "Paths")
