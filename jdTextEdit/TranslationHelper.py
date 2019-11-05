import os

class TranslationHelper():
    def __init__(self, language):
        self.strings = {}
        self.language = language
        currentDir = os.path.dirname(os.path.realpath(__file__))
        self.readDirectory(os.path.join(currentDir,"translation"))
        #langPath = os.path.join(currentDir,"translation","en.lang")
        #self.readLanguageFile(langPath)
        #langPath = os.path.join(currentDir,"translation",language + ".lang")
        #if os.path.isfile(langPath):
        #    self.readLanguageFile(langPath)

    def readLanguageFile(self, path):
        with open(path,encoding="utf-8") as f:
            content = f.readlines()
            for line in content:
                if line != "\n" and line.find("#") != 0:
                    try:
                        a,b = line.rstrip().split("=",1)
                        self.strings[a] = b
                    except:
                        print('Error in line "' + line + '"')

    def readDirectory(self, path):
        self.readLanguageFile(os.path.join(path,"en_GB.lang"))
        if os.path.isfile(os.path.join(path,self.language + ".lang")):
            self.readLanguageFile(os.path.join(path,self.language + ".lang"))

    def translate(self, key):
        if key in self.strings:
            return self.strings[key]
        else:
            return key
