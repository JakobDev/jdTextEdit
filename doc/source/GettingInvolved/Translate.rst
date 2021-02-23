==========================
Translate jdTextEdit
==========================

jdTextEdit stores it's translation in .lang files. They are currently located on the following places:

* jdTextEdit/translation
* jdTextEdit/plugins/SpellChecker/translation
* jdTextEdit/plugins/pluginmanager/translation

Start Translation
-------------------------------------------------------

To start a translation just copy a .lang file in a language you speak (in most cases english) and rename it to your_language_code.lang. Open the file and edit it. Start jdTextEdit and open the Settings Window. Now you should see your language in the drop down list.

As you may notice, your language is shown by the language code in the list. To change that edit the lines which starts with language. at the start of the .lang file. Add your language here. You should do that with the en_us.lang as well.

Upstream Translation
-------------------------------------------------------
To upstream your translation please make a Merge Request at the `GitLab Repo of jdTextEdit <https://gitlab.com/JakobDev/jdTextEdit>`_.
