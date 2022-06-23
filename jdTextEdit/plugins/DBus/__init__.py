from PyQt6.QtCore import QCoreApplication, QObject, pyqtClassInfo, pyqtSlot
from PyQt6.QtDBus import QDBusConnection, QDBusAbstractAdaptor
import sys
import os


with open(os.path.join(os.path.dirname(__file__), "interface.xml"), "r", encoding="utf-8") as f:
    interface = f.read()

@pyqtClassInfo('D-Bus Interface', 'com.gitlab.JakobDev.jdTextEdit')
@pyqtClassInfo('D-Bus Introspection', interface)
class Service(QDBusAbstractAdaptor):

    def __init__(self, env, parent):
        super().__init__(parent)
        QDBusConnection.sessionBus().registerObject("/", parent)

        if not QDBusConnection.sessionBus().registerService("com.gitlab.JakobDev.jdTextEdit"):
            print(QDBusConnection.sessionBus().lastError().message(), file=sys.stderr)

        self._env = env

    @pyqtSlot(str)
    def OpenFile(self, path):
        self._env.pluginAPI.openFile(path)

    @pyqtSlot(result=str)
    def GetVersion(self):
        return self._env.version


def main(env):
    if not QDBusConnection.sessionBus().isConnected():
        print ("Cannot connect to the D-Bus session bus.\nPlease check your system settings and try again.", file=sys.stderr);

    service = Service(env, env.app)
