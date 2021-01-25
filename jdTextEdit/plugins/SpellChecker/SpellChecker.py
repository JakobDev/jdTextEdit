from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import QColor, QCursor
from PyQt5.QtCore import QObject
import enchant
import os

class SpellChecker(QObject):
    def __init__(self,env,settings):
        super().__init__()
        self.env = env
        self.settings = settings
        self.update_language()

    def update_language(self):
        if self.settings.spellCheckingEnableCustomPwl:
            self.dict = enchant.DictWithPWL(self.settings.spellCheckingLanguage.self.settings.spellCheckingCustomPwlPath)
        else:
            self.dict = enchant.DictWithPWL(self.settings.spellCheckingLanguage,os.path.join(self.env.dataDir,"pwl.txt"))
        self.enable_custom_pwl = self.settings.spellCheckingEnableCustomPwl
        self.custom_pwl_path = self.settings.spellCheckingCustomPwlPath
        self.current_language = self.settings.spellCheckingLanguage

    def check_line(self,editor,linenum):
        editor.clearIndicatorRange(linenum,0,linenum,editor.lineLength(linenum),editor.spell_checker_indicator)
        editor.spell_line_data[linenum] = []
        if not self.settings.spellCheckingEnabled:
            return
        linecon = editor.text(linenum)
        words = linecon.split(" ")
        startpos = 0
        for w in words:
            w = w.replace("\n","")
            endpos = startpos + len(w)
            if w != "" and not (len(w) < self.settings.spellCheckingMinimumWordLength):
                if not self.dict.check(w):
                    editor.fillIndicatorRange(linenum,startpos,linenum,endpos,editor.spell_checker_indicator)
                    editor.spell_line_data[linenum].append([startpos,endpos,w,linenum,editor])
            startpos = endpos + 1

    def editor_init_function(self,editor):
        editor.spell_checker_indicator = editor.getIndicatorNumber()
        editor.setIndicatorForegroundColor(QColor("red"),editor.spell_checker_indicator)
        editor.enable_spell_checking = self.settings.spellCheckingEnabled
        editor.spell_checking_language = self.settings.spellCheckingLanguage
        editor.spell_checking_minum_word_length = self.settings.spellCheckingMinimumWordLength
        editor.spell_checking_enable_custom_pwl = self.settings.spellCheckingEnableCustomPwl
        editor.spell_checking_custom_pwl_path = self.settings.spellCheckingCustomPwlPath
        editor.spell_line_data = {}

    def open_file_function(self,editor):
        if editor.isBigFile():
            return
        for linenum in range(0,editor.lines()):
            self.check_line(editor,linenum)

    def restore_session_function(self,editor,data):
        if editor.isBigFile():
            return
        for linenum in range(0,editor.lines()):
            self.check_line(editor,linenum)

    def text_changed_function(self,editor):
        linenum = editor.cursorPosLine
        self.check_line(editor,linenum)

    def application_settings_updated(self,settings):
        self.settings = settings
        if self.current_language != settings.spellCheckingLanguage or self.enable_custom_pwl != settings.spellCheckingEnableCustomPwl or self.custom_pwl_path != settings.spellCheckingCustomPwlPath:
            self.update_language()

    def editor_settings_updated(self,editor,settings):
        if editor.spell_checking_language != self.settings.spellCheckingLanguage or \
        editor.enable_spell_checking != self.settings.spellCheckingEnabled or \
        editor.spell_checking_minum_word_length != self.settings.spellCheckingMinimumWordLength or \
        editor.spell_checking_enable_custom_pwl != self.settings.spellCheckingEnableCustomPwl or \
        editor.spell_checking_custom_pwl_path != self.settings.spellCheckingCustomPwlPath:
            for linenum in range(0,editor.lines()):
                self.check_line(editor,linenum)

    def language_changed_function(self,editor,langauge):
        if editor.isBigFile():
            return
        for linenum in range(0,editor.lines()):
            self.check_line(editor,linenum)

    def context_menu_function(self,editor,event):
        if editor.hasSelectedText():
            return
        position = editor.positionFromPoint(event.pos())
        if position == -1:
            return
        line, index = editor.lineIndexFromPosition(position)
        for i in editor.spell_line_data[line]:
            if i[0] < index and i[1] >= index:
                self.show_context_menu(i,editor)
                event.accept()

    def show_context_menu(self,data,editor):
        self.menu = QMenu()

        suggestions = self.dict.suggest(data[2])
        for i in suggestions:
            action = QAction(i,self)
            action.setData(data + [i])
            action.triggered.connect(self.spell_suggest_clicked)
            self.menu.addAction(action)

        if len(suggestions) !=0:
            self.menu.addSeparator()

        add_action = QAction(self.env.translate("plugin.spellChecker.contextMenu.addToDict"),self)
        add_action.triggered.connect(self.add_word_clicked)
        add_action.setData(data)
        self.menu.addAction(add_action)

        self.menu.popup(QCursor.pos())

    def spell_suggest_clicked(self):
        action = self.sender()
        if action:
            data = action.data()
            data[4].setSelection(data[3],data[0],data[3],data[1])
            data[4].replaceSelectedText(data[5])

    def add_word_clicked(self):
        action = self.sender()
        if action:
            data = action.data()
            self.dict.add_to_pwl(data[2])
            self.check_line(data[4],data[3])
