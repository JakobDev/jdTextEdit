from jdTextEdit.api.SignalBase import SignalBase

class EditorSignals():
    def __init__(self):
        self.editorInit = SignalBase()
        self.openFile = SignalBase()
        self.linesChanged = SignalBase()
        self.textChanged = SignalBase()
        self.indicatorClicked = SignalBase()
        self.indicatorReleased = SignalBase()
        self.contextMenu = SignalBase()
        self.settingsChanged = SignalBase()
        self.languageChanged = SignalBase()
        self.saveSession = SignalBase()
        self.restoreSession = SignalBase()
