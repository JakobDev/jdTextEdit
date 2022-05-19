class StatusBarWidgetBase():
    @staticmethod
    def getID() -> str:
        return "unknown"

    @staticmethod
    def getName() -> str:
        return "Unknown"

    def updateWidget(self, mainWindow):
        pass

