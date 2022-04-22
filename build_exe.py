#!/usr/bin/env python3
from cx_Freeze import setup, Executable
import platform
import os


with open(os.path.join(os.path.dirname(__file__), "jdTextEdit", "version.txt"), "r", encoding="utf-8") as f:
    version = f.read().strip()

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
    version = version,
    description = "A powerful texteditor with a lot of features'",
    options = {"build_exe": build_exe_options},
    executables = [target]
)
