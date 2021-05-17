from jdTextEdit.api.SignalBase import SignalBase

class TabWidgetSignals():
    def __init__(self):
        self.tabCreated = SignalBase()
        self.tabClosed = SignalBase()
