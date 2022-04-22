#!/usr/bin/env python3
from setuptools.command.build_py import build_py
from setuptools import find_packages, setup
from typing import Optional
import subprocess
import shutil
import sys
import os


def get_lrelease_command() -> Optional[str]:
    for i in ("lrelease", "pyside6-lrelease", "pyside5-lrelease"):
        if shutil.which(i) is not None:
            return i
    return None


class BuildTranslations(build_py):
    def run(self):
        command = get_lrelease_command()
        if command is None:
            print("lrelease not found", file=sys.stderr)
            sys.exit(1)
        translation_source_dir = os.path.join("jdTextEdit", "i18n")
        translation_bin_dir = os.path.join(self.build_lib, "jdTextEdit", "i18n")
        if not os.path.isdir(translation_bin_dir):
            os.makedirs(translation_bin_dir)
        for i in os.listdir(translation_source_dir):
            if i.endswith(".ts"):
                subprocess.run([command, os.path.join(translation_source_dir, i), "-qm", os.path.join(translation_bin_dir, i[:-3] + ".qm")])
        super().run()


with open(os.path.join(os.path.dirname(__file__), "jdTextEdit", "version.txt"), "r", encoding="utf-8") as f:
    version = f.read().strip()

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(name="jdTextEdit",
    version=version,
    description=" A powerful texteditor with a lot of features",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="JakobDev",
    author_email="jakobdev@gmx.de",
    url="https://gitlab.com/JakobDev/jdTextEdit",
    download_url="https://gitlab.com/JakobDev/jdTextEdit/-/releases",
    python_requires=">=3.8",
    include_package_data=True,
    install_requires=[
        "PyQt6",
        "PyQt6-QScintilla",
        "chardet",
        "requests",
        "jdTranslationHelper",
        "EditorConfig",
        "pyenchant"
    ],
    extras_require = {
        "Use cchardet as encoding detector ":  ["cchardet"],
        "Use charset_normalizer as encoding detector ":  ["charset_normalizer"]
    },
    packages=find_packages(),
    entry_points={
        "console_scripts": ["jdTextEdit = jdTextEdit.jdTextEdit:main"]
    },
    cmdclass={
        "build_py": BuildTranslations,
    },
    license="GPL v3",
    keywords=["JakobDev","QScintilla","PyQt","PyQt5","Editor","Texteditor","Macro"],
    project_urls={
        "Issue tracker": "https://gitlab.com/JakobDev/jdTextEdit/-/issues",
        "Documentation": "https://jdtextedit.readthedocs.io"
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Environment :: Other Environment",
        "Environment :: X11 Applications :: Qt",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Natural Language :: German",
        "Topic :: Text Editors",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
 )
