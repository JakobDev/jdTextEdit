from PyQt6.QtDBus import QDBusConnection, QDBusAbstractAdaptor
from PyQt6.QtCore import pyqtClassInfo, pyqtSlot
from typing import TYPE_CHECKING
import os


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


with open(os.path.join(os.path.dirname(__file__), "interface.xml"), "r", encoding="utf-8") as f:
    interface = f.read()

@pyqtClassInfo("D-Bus Interface", "page.codeberg.JakobDev.jdTextEdit")
@pyqtClassInfo("D-Bus Introspection", interface)
class Service(QDBusAbstractAdaptor):
    def __init__(self, env: "Environment") -> None:
        super().__init__(env.app)
        QDBusConnection.sessionBus().registerObject("/", env.app)

        if not QDBusConnection.sessionBus().registerService("page.codeberg.JakobDev.jdTextEdit"):
            env.logger.error(QDBusConnection.sessionBus().lastError().message())

        self._env = env

    @pyqtSlot(str)
    def OpenFile(self, path) -> None:
        self._env.pluginAPI.openFile(path)

    @pyqtSlot(result=str)
    def GetVersion(self) -> str:
        return self._env.version


def main(env: "Environment") -> None:
    if not QDBusConnection.sessionBus().isConnected():
        env.logger.error("Cannot connect to the D-Bus session bus. Please check your system settings and try again.")
        return

    Service(env)
