from PyQt6.QtWidgets import QWidget, QRadioButton, QLineEdit, QLabel, QVBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt6.QtCore import QCoreApplication
from jdTextEdit.Settings import Settings


class TerminalEmulatorTab(QWidget, SettingsTabBase):
    def __init__(self, env):
        super().__init__()

        self._systemEmulatorButton = QRadioButton(QCoreApplication.translate("TerminalEmulatorTab", "Use system terminal emulator"))
        self._customEmulatorButton = QRadioButton(QCoreApplication.translate("TerminalEmulatorTab", "Use custom terminal emulator"))
        self._customEmulatorEdit = QLineEdit()

        self._customEmulatorEdit.setPlaceholderText(QCoreApplication.translate("TerminalEmulatorTab", "The executable name e.g. xterm"))

        self._customEmulatorButton.toggled.connect(self._updateEditEnabled)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel(QCoreApplication.translate("TerminalEmulatorTab", "You can set the terminal emulator that is used when executing commands here")))
        mainLayout.addWidget(self._systemEmulatorButton)
        mainLayout.addWidget(self._customEmulatorButton)
        mainLayout.addWidget(self._customEmulatorEdit)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def _updateEditEnabled(self):
        self._customEmulatorEdit.setEnabled(self._customEmulatorButton.isChecked())

    def updateTab(self, settings: Settings):
        if settings.get("useCustomTerminalEmulator"):
            self._customEmulatorButton.setChecked(True)
        else:
            self._systemEmulatorButton.setChecked(True)
        self._customEmulatorEdit.setText(settings.get("customTerminalEmulator"))
        self._updateEditEnabled()

    def getSettings(self, settings: Settings):
        settings.set("useCustomTerminalEmulator", self._customEmulatorButton.isChecked())
        settings.set("customTerminalEmulator", self._customEmulatorEdit.text())

    def title(self) -> str:
        return QCoreApplication.translate("TerminalEmulatorTab", "Terminal emulator")
