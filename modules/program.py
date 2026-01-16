from getpass import getpass
import os
from time import sleep

from dotenv import load_dotenv

from config.settings import PATHS
from modules.English_DB import English_DB
from modules.Interface import clear_terminal
from modules.Telegram import test_token
from modules.files import create_env_file


def get_info():
    load_dotenv(dotenv_path=PATHS.env)
    token_bot = os.getenv('TOKEN')
    db_username = os.getenv('DB_USERNAME')
    db_password = os.getenv('DB_PASSWORD')
    
    if not (token_bot and db_username and db_password):
        token_bot = get_token()
        db_username, db_password = get_db_user_info()
        ask_to_save_data(token_bot, db_username, db_password)

    return token_bot, db_username, db_password


def get_token():
    while True:
        api_key = get_input('Enter your bot token',
                            password=True)
        if test_token(api_key):
            return api_key
        else:
            print('Invalid token. Please try again.')
            sleep(2)


def get_db_user_info():
    while True:
        name = get_input('Enter your database username:\n > ')
        password = get_input('Enter your database password', password=True)

        if English_DB().test_connection(name, password) == 'Exists':
            return name, password

        print('Invalid username or password. Please try again.')
        sleep(2)


def ask_to_save_data(token, db_username, db_password):
    while True:
        save_data = get_input('Save token, name and password locally? (y/n)\n > ')
        if save_data.lower() == 'y':
            save_user_data(token, db_username, db_password)
            return True
        elif save_data.lower() == 'n':
            return False
        else:
            print('Invalid input. Please try again.')
            sleep(1.3)


def save_user_data(token, username, password):
    template =f'''\
TOKEN={token}
DB_USERNAME={username}
DB_PASSWORD={password}'''
    create_env_file(PATHS.env, template)


def get_input(prefix='\n > ', password=False,
              clear_screen=True):
    while True:
        if clear_screen:
            clear_terminal()
        if password:
            user_input = getpass(prefix).strip()
        else:
            user_input = input(prefix).strip()

        return user_input