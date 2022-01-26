from jdTextEdit.api.SignalBase import SignalBase


class ProjectSignals():
    def __init__(self):
        self.directoryChanged = SignalBase()
        self.projectAdded = SignalBase()
        self.projectDeleted = SignalBase()
