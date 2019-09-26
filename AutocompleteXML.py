from PyQt5.Qsci import QsciAPIs
from xml.dom import minidom

class AutocompleteXML(QsciAPIs):
    def __init__(self,lexer,path):
        super().__init__(lexer)
        apidoc = minidom.parse(path)
        apilist = apidoc.getElementsByTagName("KeyWord")
        for i in apilist:
            self.add(i.attributes['name'].value)
        self.prepare()
