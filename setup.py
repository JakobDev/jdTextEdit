#!/usr/bin/env python3
from setuptools import find_packages, setup

setup(name='jdTextEdit',
    version='8.1',
    description=' A powerful texteditor with a lot of features',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author='JakobDev',
    author_email='jakobdev@gmx.de',
    url='https://gitlab.com/JakobDev/jdTextEdit',
    download_url='https://gitlab.com/JakobDev/jdTextEdit/-/releases',
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=[
        'PyQt5',
        'QScintilla',
        'chardet',
        'requests',
        'jdTranslationHelper',
        'charset_normalizer',
        'cchardet',
        'EditorConfig',
        'pyenchant'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': ['jdTextEdit = jdTextEdit.jdTextEdit:main']
    },
    license='GPL v3',
    keywords=['JakobDev','QScintilla','PyQt','PyQt5','Editor','Texteditor','Macro'],
    project_urls={
        'Issue tracker': 'https://gitlab.com/JakobDev/jdTextEdit/-/issues',
        'Documentation': 'https://jdtextedit.readthedocs.io'
    },

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Other Environment',
        'Environment :: X11 Applications :: Qt',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Natural Language :: German',
        'Topic :: Text Editors',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
 )
