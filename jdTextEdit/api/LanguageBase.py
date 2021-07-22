from PyQt6.Qsci import QsciLexer, QsciAPIs
from PyQt6.QtGui import QIcon
from typing import List

class LanguageBase():
    def getLexer(self) -> QsciLexer:
        """
        Returns the lexer of the language
        :return: lexer
        """
        return None

    def getName(self) -> str:
        """
        Retruns the name of the language, which is used to display it
        :return: name
        """
        return "Unknown"

    def getExtensions(self) -> List[str]:
        """
        Returns alist of known extension for the language e.g. py
        :return: list of extensions
        """
        return []

    def getStarttext(self) -> List[str]:
        """
        Returns a list of text, which files usually starts e.g. #!/usr/bin/python
        :return:
        """
        return []

    def getID(self) -> str:
        """
        Returns the id of the language, which is used to identify the language intern
        :return: id
        """
        return "unknown"

    def getAPI(self,lexer: QsciLexer) -> QsciAPIs:
        """
        Returns the API of the language which is used for Autocompletion
        :param lexer: the current lexer
        :return: the API
        """
        return None

    def getIcon(self) -> QIcon:
        """
        Returns the Icon of the language, which is displayed in the menu. returns None, if the language has no Icon.
        :return: icon
        """
        return None
