#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(name='jdTextEdit',
    version='4.0',
    description=' A powerful texteditor with a lot of features .',
    author='JakobDev',
    author_email='jakobdev@gmx.de',
    url='https://gitlab.com/JakobDev/jdTextEdit',
    include_package_data=True,
    install_requires=[
        'PyQt5',
        'QScintilla',
        'chardet'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': ['jdTextEdit = jdTextEdit.jdTextEdit:main']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Text Editors',
    ],
 )
