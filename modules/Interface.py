import os
import platform
from telebot import types

from config.settings import PATHS
from modules.files import read_json_file


MACHINE_PLATFORM = {
    "OS": platform.system(),
}


class Interface:
    def __init__(self):
        self.BEGIN = '/learn'
        self.ADD_WORD = '/add word'
        self.DELETE_WORD = '/remove'
        self.SWITCH_MODE = '/switch mode'
        self.NEXT = '/next'
        self.END = '/end'

        self._learn_set = [self.DELETE_WORD,
                           self.END,
                           self.NEXT]

        self.greeting = "Hey there, let\'s learn English"

    def menu(self):
        markup = types.ReplyKeyboardMarkup(row_width=2)

        return markup.add(*[types.KeyboardButton(word) for word in 
                [self.ADD_WORD,
                 self.SWITCH_MODE,
                 self.BEGIN,
                 ]])

    def learn(self, words_list=None, remove_commands=None):
        '''Return a keyboard with words if added and default command buttons
        in this mode. The command buttons might be removed (poped) by 
        assigning their ids into remove_button as a list.'''
        if words_list is None:
            words_list = []
        
        current_commands = self._learn_set.copy()
        if remove_commands:
            for button in remove_commands:
                current_commands.pop(button)

        markup = types.ReplyKeyboardMarkup(row_width=2)
        words_list.extend(current_commands)

        return markup.add(*[types.KeyboardButton(word) for word in words_list])
    
    def no_keyboard(self):
        return types.ReplyKeyboardRemove()
    
    def error_decode(self, error_code):
        error_dict = read_json_file(PATHS.errors_terms)
        return error_dict[error_code]


def clear_terminal():
    if MACHINE_PLATFORM['OS'] == 'Linux':
        os.system('clear')
    elif MACHINE_PLATFORM['OS'] == 'Windows':
        os.system('cls')