from jdTextEdit.api.LanguageBase import LanguageBase
from jdTextEdit.AutocompleteXML import AutocompleteXML
import os

class BuiltinLanguage(LanguageBase):
    def __init__(self,env,entry):
        self.env = env
        self.list_entry = entry

    def getLexer(self):
        return self.list_entry["lexer"]()

    def getName(self) -> str:
        return self.list_entry["name"]

    def getID(self) -> str:
        return "builtin." + self.list_entry["name"]

    def getExtensions(self):
        return self.list_entry["extension"]

    def getStarttext(self):
        if "startswith" in self.list_entry:
            return self.list_entry["startswith"]
        else:
            return []

    def getAPI(self,lexer):
        if self.list_entry["xmlapi"] == "":
            return
        path = os.path.join(self.env.programDir,"autocompletion",self.list_entry["xmlapi"] + ".xml")
        return AutocompleteXML(lexer,path)
