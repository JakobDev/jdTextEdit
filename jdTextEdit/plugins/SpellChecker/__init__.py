from .SpellCheckingTab import SpellCheckingTab
from .SpellChecker import SpellChecker
from typing import TYPE_CHECKING
from PyQt6.QtCore import QLocale
import os


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


def main(env: "Environment") -> None:
    currentDir = os.path.dirname(os.path.realpath(__file__))
    env.pluginAPI.addTranslationDirectory(os.path.join(currentDir, "translations"))

    env.pluginAPI.registerSetting("spellCheckingLanguage", QLocale.system().name())
    env.pluginAPI.registerSetting("spellCheckingCustomPwlPath", os.path.join(env.dataDir, "pwl.txt"))
    env.pluginAPI.registerSetting("spellCheckingEnableCustomPwl", False)
    env.pluginAPI.registerSetting("spellCheckingEnabled", False)
    env.pluginAPI.registerSetting("spellCheckingMinimumWordLength", 3)
    env.pluginAPI.registerSetting("spellCheckingDisableBigFiles", True)

    env.pluginAPI.addBigFilesCheckBox("spellCheckingDisableBigFiles", env.translate("plugin.spellChecker.bigFilesSetting"))

    env.pluginAPI.addSettingsTab(SpellCheckingTab(env))

    application_signals = env.pluginAPI.getApplicationSignals()

    s = SpellChecker(env,env.settings)
    editor_signals = env.pluginAPI.getEditorSignals()
    editor_signals.editorInit.connect(s.editor_init_function)
    editor_signals.openFile.connect(s.open_file_function)
    editor_signals.restoreSession.connect(s.restore_session_function)
    editor_signals.textChanged.connect(s.text_changed_function)
    application_signals.settingsChanged.connect(s.application_settings_updated)
    editor_signals.settingsChanged.connect(s.editor_settings_updated)
    editor_signals.languageChanged.connect(s.language_changed_function)
    editor_signals.contextMenu.connect(s.context_menu_function)
