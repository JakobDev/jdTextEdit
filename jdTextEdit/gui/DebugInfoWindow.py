from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt6.Qsci import QsciScintilla, QsciLexerJSON
from jdTextEdit.Functions import restoreWindowState
from PyQt6.QtCore import QCoreApplication
import platform
import json
import sys


class DebugInfoWindow(QWidget):
    def __init__(self, env):
        super().__init__()
        self.env = env

        self._dataShowWidget = QsciScintilla()
        copyButton = QPushButton(QCoreApplication.translate("DebugInfoWindow", "Copy to Clipboard"))
        closeButton = QPushButton(QCoreApplication.translate("DebugInfoWindow", "Close"))

        jsonLexer = QsciLexerJSON(self._dataShowWidget)
        self._dataShowWidget.setLexer(jsonLexer)
        self._dataShowWidget.setReadOnly(True)

        copyButton.clicked.connect(lambda: QApplication.clipboard().setText(self._dataShowWidget.text()))
        closeButton.clicked.connect(self.close)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(copyButton)
        buttonLayout.addWidget(closeButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self._dataShowWidget)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(QCoreApplication.translate("DebugInfoWindow", "Debug Information"))

        self.resize(600, 600)

        restoreWindowState(self, self.env.windowState, "DebugInfoWindow")

    def openWindow(self):
        data = {}
        data["version"] = self.env.version
        data["dataDir"] = self.env.dataDir
        data["programDir"] = self.env.programDir
        data["operatingSystem"] = platform.platform()
        data["pythonVersion"] = platform.python_version()
        data["pythonPath"] = sys.executable
        data["commandlineArguments"] = sys.argv[1:]
        data["plugins"] = list(self.env.plugins.keys())
        data["settings"] = self.env.settings.getAll()
        data["distributionSettings"] = self.env.distributionSettings
        data["updaterEnabled"] = self.env.enableUpdater

        self._dataShowWidget.setText(json.dumps(data, ensure_ascii=False, indent=4))

        self.show()
