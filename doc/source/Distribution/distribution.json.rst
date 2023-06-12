==========================
distribution.json
==========================

distribution.json is a JSON file which is placed in the Program Directory. It has some options for people who are building packages. Currently the following options are available:

You don't need to set all options. Just set the options you need and remove the others from the file.

You can use enviroment variables in all paths.

.. code:: json

    {
        "enableUpdater": false,
        "_description_": "Enable or disable the updater",

        "dataDirectory": "~/.edit",
        "_description_": "Sets the Data Directory.",

        "aboutMessage": "Hello from John Doe",
        "_description_": "This message is shown in the About Window.",

        "templateDirectories": [],
        "_description_": "Add template directories",

        "enableTranslationWarning": false,
        "_description_": "Show a warning when no language is build"
    }
