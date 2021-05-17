import traceback

class SignalBase():
    def __init__(self):
        self.functionList = []

    def connect(self,func):
        self.functionList.append(func)

    def emit(self,*arg):
        for i in self.functionList:
            try:
                i(*arg)
            except Exception as e:
                print(traceback.format_exc(),end="")
