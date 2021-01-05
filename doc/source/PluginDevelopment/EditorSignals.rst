==========================
Editor Signals
==========================

editorInit
    Emited when a Editor Widget is created

    Arguments
        - CodeEdit: The Widget which is created

openFile
    Emited when a File is opened

    Arguments
        - CodeEdit: The Widget whre the file is opened
        - str: The path of the file

linesChanged
    Emited when the a line is changed. Same as the QScintilla Signal.

    Arguments
        - CodeEdit: The Widget where the Line is changed

textChanged
    Emited when the Text is changed. Same as the QScintilla Signal.

    Arguments
        - CodeEdit: The Widget where the Text is changed

indicatorClicked
    Emited when a indicator is clicked is changed. Same as the QScintilla Signal.

    Arguments
        - CodeEdit: The Widget where the indicatir is clicked
        - int: Line
        - iint Index
        - Qt::KeyboardModifiers: state

indicatorReleased
    Emited when a indicator is clicked is released. Same as the QScintilla Signal.

    Arguments
        - CodeEdit: The Widget where the indicatir is realeased
        - int: Line
        - iint Index
        - Qt::KeyboardModifiers: state

contextMenu
    Emited when a the user try to open a context menu. Accept the event that given as arg to prevent the original menu to open, so you can create your own menu.

    Arguments
        - CodeEdit: The Widget where the menu is opened
        - QEvent: The context menu event

settingsChanged
    Emited when a the settingsof a widget are changed.

    Arguments
        - CodeEdit: The Widget where the settings are changed
        - Settings: The new settings
