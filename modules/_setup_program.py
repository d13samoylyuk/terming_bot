from modules.files import check_file_exists, create_folder, write_file
from config.settings import PATHS


sys_files_contents = {
    PATHS.configs: ('{'
        '"switched_mode": []'
    '}'),
}


def setup_program():
    '''
    Check if exists and create files:
    - file "config.json"
    '''
    
    for path, content in sys_files_contents.items():
        if not check_file_exists(path):
            write_file(path, content)


def integrity_check():
    pass