===================
Add Language
===================

To add a new language you need to create a class that inherit from LanguageBase.

.. code:: python

    from jdTextEdit.api.LanguageBase import LanguageBase
    from PyQt5.Qsci import QsciLexerPython, QsciAPIs

    class MyLanguage(LanguageBase):
        def getLexer(self):
            return QsciLexerPython()

        def getName(self):
            return "My Language"

        def getID(self):
            return "myplugin.mylanguage"

        def getExtensions(self):
            return ["py"]

        def getStarttext(self):
            return ["#!/usr/bin/python"]

        def getAPI(self,lexer):
            api = QsciAPIs(lexer)
            api.add("Hello")
            api.prepare()

Here's a description of all functions

.. code:: python

    getLexer()

Returns a QsciScintilla Lexer. You can use a existing one or write one by yourself.

.. code:: python

    getName()

Retruns the Name of your Language.

.. code:: python

    getID()

Returns the ID of your Language. The ID is used to identify your Lanmguage, so make sure it is used by nobody else.

The following functions are optional.

.. code:: python

    getExtensions()

Returns a list with all extension for you filetype. e.g. if the list contains "mylang" and the user open a file with the name "text.mylang" your language will be set.

.. code:: python

    getStarttext()

Some language starts every or the moist time with a special text. e.g. all XML files start with <?xml. This function returns a list which all known starttexts for your language.

.. code:: python

    getAPI(lexer)

Retruns the API for the language.
