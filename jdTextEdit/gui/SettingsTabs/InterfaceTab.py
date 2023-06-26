from PyQt6.QtWidgets import QWidget, QComboBox, QLabel, QCheckBox, QLineEdit, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QStyleFactory, QMessageBox
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from jdTextEdit.Functions import selectComboBoxItem
from PyQt6.QtCore import QCoreApplication
from jdTextEdit.Settings import Settings
from typing import TYPE_CHECKING
import time


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


class InterfaceTab(QWidget, SettingsTabBase):
    def __init__(self, env: "Environment") -> None:
        super().__init__()
        self.env = env

        self.styleSelectComboBox = QComboBox()
        self.settingsWindowType = QComboBox()
        self.swapOkCancel = QCheckBox(QCoreApplication.translate("InterfaceTab", "Swap position of OK and Cancel (needs restart)"))
        self.enableUserChrome = QCheckBox(QCoreApplication.translate("InterfaceTab", "Enable loading of userChrome.css"))
        self.useCustomDateTimeFormat = QCheckBox(QCoreApplication.translate("InterfaceTab", "Use custom Datetime format"))
        self.customDateTimeFormatEdit = QLineEdit()
        customDateTimeFormatPreviewButton = QPushButton(QCoreApplication.translate("InterfaceTab", "Preview"))

        self.styleSelectComboBox.addItem(QCoreApplication.translate("InterfaceTab", "System style"))
        self.styleSelectComboBox.addItems(QStyleFactory.keys())

        self.settingsWindowType.addItem(QCoreApplication.translate("InterfaceTab", "Modern"))
        self.settingsWindowType.addItem(QCoreApplication.translate("InterfaceTab", "Classic"))

        self.useCustomDateTimeFormat.stateChanged.connect(self._updateDateTimeFormatLayout)
        customDateTimeFormatPreviewButton.clicked.connect(self._previewCustomDateTimeFormat)

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(QCoreApplication.translate("InterfaceTab", "Application style:")), 0, 0)
        gridLayout.addWidget(self.styleSelectComboBox, 0, 1)
        gridLayout.addWidget(QLabel(QCoreApplication.translate("InterfaceTab", "Settings Design (needs restart):")), 1, 0)
        gridLayout.addWidget(self.settingsWindowType, 1, 1)

        self.dateTimeFormatLayout = QHBoxLayout()
        self.dateTimeFormatLayout.addWidget(QLabel(QCoreApplication.translate("InterfaceTab", "Format:")))
        self.dateTimeFormatLayout.addWidget(self.customDateTimeFormatEdit)
        self.dateTimeFormatLayout.addWidget(customDateTimeFormatPreviewButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addWidget(self.swapOkCancel)
        mainLayout.addWidget(self.enableUserChrome)
        mainLayout.addWidget(self.useCustomDateTimeFormat)
        mainLayout.addLayout(self.dateTimeFormatLayout)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def _updateDateTimeFormatLayout(self) -> None:
        for i in range(self.dateTimeFormatLayout.count()):
            self.dateTimeFormatLayout.itemAt(i).widget().setEnabled(self.useCustomDateTimeFormat.isChecked())

    def _previewCustomDateTimeFormat(self) -> None:
        try:
            QMessageBox.information(self, QCoreApplication.translate("InterfaceTab", "Preview"), time.strftime(self.customDateTimeFormatEdit.text()))
        except ValueError:
            QMessageBox.warning(self, QCoreApplication.translate("InterfaceTab", "Format invalid"), QCoreApplication.translate("InterfaceTab", "This format is not valid"))

    def updateTab(self, settings: Settings) -> None:
        applicationStyle = settings.get("applicationStyle")

        if applicationStyle == "default":
            self.styleSelectComboBox.setCurrentIndex(0)
        else:
            selectComboBoxItem(self.styleSelectComboBox, applicationStyle)

        if settings.get("settingsWindowUseModernDesign"):
            self.settingsWindowType.setCurrentIndex(0)
        else:
            self.settingsWindowType.setCurrentIndex(1)

        self.swapOkCancel.setChecked(settings.get("swapOkCancel"))
        self.enableUserChrome.setChecked(settings.get("enableUserChrome"))
        self.useCustomDateTimeFormat.setChecked(settings.get("useCustomDateTimeFormat"))
        self.customDateTimeFormatEdit.setText(settings.get("customDateTimeFormat"))
        self._updateDateTimeFormatLayout()

    def getSettings(self, settings: Settings) -> None:
        if self.styleSelectComboBox.currentIndex() == 0:
            settings.set("applicationStyle","default")
        else:
            settings.applicationStyle = self.styleSelectComboBox.itemText(self.styleSelectComboBox.currentIndex())

        if self.settingsWindowType.currentIndex() == 0:
            settings.set("settingsWindowUseModernDesign", True)
        else:
            settings.set("settingsWindowUseModernDesign", False)

        settings.set("swapOkCancel", self.swapOkCancel.isChecked())
        settings.set("useCustomDateTimeFormat", self.useCustomDateTimeFormat.isChecked())
        settings.set("customDateTimeFormat", self.customDateTimeFormatEdit.text())

    def title(self) -> str:
        return QCoreApplication.translate("InterfaceTab", "Interface")