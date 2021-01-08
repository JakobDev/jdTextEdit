==========================
distribution.json
==========================

distribution.json is a JSON file which is placed in the Program Directory. It has some options for people who are building packages. Currently the following options are available:

.. code:: json

    {
        "enableUpdater": false,
        "_description_": "Enable or disable the updater",

        "dataDirectory": "~/.edit",
        "_description_": "Sets the Data Directory. Use ~ as placeholder for the home directory",

        "aboutMessage": "Hello from John Doe",
        "_description_": "This message is shown in the About Window."
    }
