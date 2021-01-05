class SignalBase():
    def __init__(self):
        self.function_list = []

    def connect(self,func):
        self.function_list.append(func)

    def emit(self,*arg):
        for i in self.function_list:
            i(*arg)
