from jdTextEdit.core.Logger import getGlobalLogger


class SignalBase():
    def __init__(self):
        self.functionList = []

    def connect(self, func):
        self.functionList.append(func)

    def emit(self, *arg):
        for i in self.functionList:
            try:
                i(*arg)
            except Exception as ex:
                getGlobalLogger().exception(ex)
