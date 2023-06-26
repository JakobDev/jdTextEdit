from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QScrollArea, QKeySequenceEdit, QGridLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.Functions import sortActionDict
from PyQt6.QtCore import QCoreApplication
from jdTextEdit.Settings import Settings
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class ResetButton(QPushButton):
    def __init__(self, text: str, keySequenceEdit: QKeySequenceEdit, defaultKeySequence: str) -> None:
        super().__init__(text)
        self.keySequenceEdit = keySequenceEdit
        self.defaultKeySequence = defaultKeySequence
        self.clicked.connect(lambda: self.keySequenceEdit.setKeySequence(self.defaultKeySequence))


class ShortcutTab(QScrollArea, SettingsTabBase):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env

    def updateTab(self, settings: Settings) -> None:
        for i in self.shortcutList:
            if i[0] in settings.shortcut:
                i[1].setKeySequence(settings.shortcut[i[0]])
            else:
                i[1].setKeySequence("")

    def getSettings(self, settings: Settings) -> None:
        for i in self.shortcutList:
            if not i[1].keySequence().isEmpty():
                settings.shortcut[i[0]] = i[1].keySequence().toString()
            elif i[0] in settings.shortcut:
                del settings.shortcut[i[0]]

    def setup(self) -> None:
        self.shortcutList: list[tuple[str, QKeySequenceEdit]] = []
        mainLayout = QGridLayout()
        self.scrollWidget = QWidget()
        defaultSettings = Settings()
        resetString = QCoreApplication.translate("ShortcutTab", "Reset")
        count = 0
        for key, value in sortActionDict(self.env.menuActions).items():
            if key == "separator":
                continue

            if value.text().startswith("&"):
                mainLayout.addWidget(QLabel(value.text().removeprefix("&")), count, 0)
            else:
                mainLayout.addWidget(QLabel(value.text()), count, 0)

            keySequenceEdit = QKeySequenceEdit()
            keySequenceEdit.setClearButtonEnabled(True)
            mainLayout.addWidget(keySequenceEdit, count, 1)
            self.shortcutList.append((key, keySequenceEdit))
            if key in defaultSettings.shortcut:
                mainLayout.addWidget(ResetButton(resetString, keySequenceEdit, defaultSettings.shortcut[key]), count, 2)
            else:
                mainLayout.addWidget(ResetButton(resetString, keySequenceEdit, ""), count, 2)
            count += 1
        self.scrollWidget.setLayout(mainLayout)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

    def title(self) -> str:
        return QCoreApplication.translate("ShortcutTab", "Shortcuts")
