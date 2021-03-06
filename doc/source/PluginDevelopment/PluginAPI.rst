===================
PluginAPI
===================

The plugin API contains the following functions:

.. code:: python

    addLanguage(language: LanguageBase)

Adds a language to jdTextEdit

.. code:: python

    getEditorSignals() -> EditorSignals:

Returns the Editor Signals.

.. code:: python

    getMainWindowSignals() -> MainWindowSignals:

Returns the Mainwindow Signals.

.. code:: python

    getApplicationSignals() -> ApplicationSignals

Returns the Application Signals.

.. code:: python

    addSettingsTab(tab: SettingsTabBase)

Adds a Settings Tab.

.. code:: python

    registerSetting(key: str,value: str)

Register a new Setting.

.. code:: python

    addTranslationDirectory(path: str)

Adds a directory which contains translations.

.. code:: python

    addBigFilesCheckBox(setting: str, text:str)

Adds a Checkbox to the Big files Settings Tab.

.. code:: python

    addTheme(theme: ThemeBase)

Adds a Theme.

.. code:: python

    addSidebarWidget(widget: SidebarWidgetBase)

Adds a Sidebar Widget.

.. code:: python

    addAction(action: QAction)

Adds a Action to the list in the settings menu.
