#!/usr/bin/env python3
from cx_Freeze import setup, Executable
import platform

build_exe_options = {"includes":["jdTextEdit.plugins.pluginmanager","jdTextEdit.plugins.SpellChecker"],"excludes": ["tkinter"]}
if platform.system() == "Windows":
    target = Executable(
        script="jdTextEdit.py",
        base="Win32GUI",
        target_name = "jdTextEdit.exe",
        icon="deploy\icon-windows.ico"
    )
else:
    target = Executable(script="jdTextEdit.py",)

setup(
    name = "jdTextEdit",
    version = "9.1",
    description = "A powerful texteditor with a lot of features'",
    options = {"build_exe": build_exe_options},
    executables = [target]
)
