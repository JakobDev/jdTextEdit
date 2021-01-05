from .SpellChecker import SpellChecker
from .SpellCheckingTab import SpellCheckingTab
import os

def main(env):
    currentDir = os.path.dirname(os.path.realpath(__file__))
    env.pluginAPI.addTranslationDirectory(os.path.join(currentDir,"translation"))

    env.pluginAPI.registerSetting("spellCheckingLanguage","de_DE")
    env.pluginAPI.registerSetting("spellCheckingCustomPwlPath",os.path.join(env.dataDir,"pwl.txt"))
    env.pluginAPI.registerSetting("spellCheckingEnableCustomPwl",False)
    env.pluginAPI.registerSetting("spellCheckingEnabled",False)
    env.pluginAPI.registerSetting("spellCheckingMinimumWordLength",3)
    env.pluginAPI.registerSetting("spellCheckingDisableBigFiles",True)

    env.pluginAPI.addBigFilesCheckBox("spellCheckingDisableBigFiles",env.translate("plugin.spellChecker.bigFilesSetting"))

    env.pluginAPI.addSettingsTab(SpellCheckingTab(env))

    application_signals = env.pluginAPI.getApplicationSignals()

    s = SpellChecker(env,env.settings)
    slots = env.pluginAPI.getEditorSignals()
    slots.editorInit.connect(s.editor_init_function)
    slots.openFile.connect(s.open_file_function)
    slots.textChanged.connect(s.text_changed_function)
    application_signals.settingsChanged.connect(s.application_settings_updated)
    slots.settingsChanged.connect(s.editor_settings_updated)
    slots.contextMenu.connect(s.context_menu_function)

def getID():
    return "builtin.spellchecker"

def getName():
    return "SpellChecker"

def getVersion():
    return "1.0"

def getAuthor():
    return "JakobDev"
