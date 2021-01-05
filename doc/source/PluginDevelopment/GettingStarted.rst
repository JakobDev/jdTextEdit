==========================
Getting Started
==========================


First create a new directory in the plugins directory with a __init__.py inside. The __init__.py must have the following functions:

.. code:: python

    def main(env):
        #Write your code here

    def getID():
        return "myPlugin"

    def getName():
        return "My Plugin"

    def getVersion():
        return "1.0"

    def getAuthor():
        return "John Doe"
