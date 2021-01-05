from jdTextEdit.api.SignalBase import SignalBase

class ApplicationSignals():
    def __init__(self):
        self.settingsChanged = SignalBase()
