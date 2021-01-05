from PyQt5.Qsci import QsciLexer, QsciAPIs
from typing import List

class LanguageBase():
    def getLexer(self) -> QsciLexer:
        return None

    def getName(self) -> str:
        return "Unknown"

    def getExtensions(self) -> List[str]:
        return []

    def getStarttext(self) -> List[str]:
        return []

    def getID(self) -> str:
        return "unknown"

    def getAPI(self,lexer: QsciLexer) -> QsciAPIs:
        return None
