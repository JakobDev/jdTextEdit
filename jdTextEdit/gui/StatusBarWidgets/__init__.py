from .CursorPosWidget import CursorPosWidget
from .LanguageWidget import LanguageWidget
from .EncodingWidget import EncodingWidget
from .LengthWidget import LengthWidget
from .PathWidget import PathWidget
from .EolWidget import EolWidget
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from jdTextEdit.Environment import Environment


def addBuiltinStatusBarWidgets(env: "Environment") -> None:
    env.pluginAPI.addStatusBarWidget(CursorPosWidget)
    env.pluginAPI.addStatusBarWidget(LanguageWidget)
    env.pluginAPI.addStatusBarWidget(EncodingWidget)
    env.pluginAPI.addStatusBarWidget(LengthWidget)
    env.pluginAPI.addStatusBarWidget(PathWidget)
    env.pluginAPI.addStatusBarWidget(EolWidget)
