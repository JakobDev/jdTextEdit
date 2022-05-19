from .CursorPosWidget import CursorPosWidget
from .LanguageWidget import LanguageWidget
from .EncodingWidget import EncodingWidget
from .PathWidget import PathWidget
from .EolWidget import EolWidget


def addBuiltinStatusBarWidgets(env):
    env.pluginAPI.addStatusBarWidget(CursorPosWidget)
    env.pluginAPI.addStatusBarWidget(LanguageWidget)
    env.pluginAPI.addStatusBarWidget(EncodingWidget)
    env.pluginAPI.addStatusBarWidget(PathWidget)
    env.pluginAPI.addStatusBarWidget(EolWidget)
