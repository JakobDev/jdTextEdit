==========================
distribution.json
==========================

distribution.json is a JSOn file which is placed in the Program Directory. It has some options for people who are bulding packages. Currenty the follwoing options are aviable:

.. code:: json

    {
        "enableUpdater": false,
        "_description_": "Enable or disable the updater",

        "dataDirectory": "~/.edit",
        "_description_": "Sets the Data Directory. Use ~ as placeholder for the home directory",

        "aboutMessage": "Hello from John Doe",
        "_description_": "This message is shown in the About Window."
    }
