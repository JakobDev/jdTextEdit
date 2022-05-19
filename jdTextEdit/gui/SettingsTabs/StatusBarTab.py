from jdTextEdit.gui.Widgets.ListSelectWidget import ListSelectWidget
from PyQt6.QtWidgets import QWidget, QTabWidget, QHBoxLayout
from jdTextEdit.api.SettingsTabBase import SettingsTabBase
from PyQt6.QtCore import QCoreApplication
from jdTextEdit.Settings import Settings


class StatusBarTab(QWidget, SettingsTabBase):
    def __init__(self, env):
        super().__init__()
        self.env = env

        self._listSelectWidgetLeft = ListSelectWidget()
        self._listSelectWidgetRight = ListSelectWidget()
        self._tabWidget = QTabWidget()

        self._tabWidget.addTab(self._listSelectWidgetLeft, QCoreApplication.translate("StatusBarTab", "Left"))
        self._tabWidget.addTab(self._listSelectWidgetRight, QCoreApplication.translate("StatusBarTab", "Right"))

        self._tabWidget.tabBar().setDocumentMode(True)
        self._tabWidget.tabBar().setExpanding(True)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self._tabWidget)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(mainLayout)

    def setup(self):
        elements = []
        for key, value in self.env.statusBarWidgetDict.items():
            elements.append([key, value.getName()])
        self._listSelectWidgetLeft.setElements(elements)
        self._listSelectWidgetRight.setElements(elements)

    def updateTab(self, settings: Settings):
        self._listSelectWidgetLeft.setSelectedIDList(settings.get("statusBarWidgetsLeft"))
        self._listSelectWidgetRight.setSelectedIDList(settings.get("statusBarWidgetsRight"))

    def getSettings(self, settings: Settings):
        settings.set("statusBarWidgetsLeft", self._listSelectWidgetLeft.getSelectedIDList())
        settings.set("statusBarWidgetsRight", self._listSelectWidgetRight.getSelectedIDList())
        return settings

    def title(self) -> str:
        return QCoreApplication.translate("StatusBarTab", "Statusbar")
