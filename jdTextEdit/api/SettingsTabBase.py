from jdTextEdit.Settings import Settings


class SettingsTabBase:
    def updateTab(self, settings: Settings):
        pass

    def getSettings(self, settings: Settings):
        pass

    def setup(self) -> None:
        pass

    def title(self) -> str:
        return "Unknown"
