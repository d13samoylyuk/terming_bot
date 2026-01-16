import csv
import os
import json


def save_json_file(file_content, file_path, ensure=True):
    slash = '/'
    if not file_path.endswith(slash) and not file_path.endswith('.json'):
        file_path = file_path + slash
    with open(file_path, 'w', encoding="utf-8") as new_j_file:
        json.dump(file_content, new_j_file, indent=4, ensure_ascii=ensure)


def read_json_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as json_file:
        return json.load(json_file)


def check_file_exists(file_path):
    return os.path.exists(file_path)


def create_env_file(path, content):
    with open(path, 'w') as env_file:
        env_file.write(content)


def delete_file(path):
    os.remove(path)


def read_csv_file(file_path):
    with open(file_path, encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        return list(reader)    


def create_folder(path, ingnor_FileExistsError=False):
    try:
        os.mkdir(path)
    except FileExistsError as error:
        if not ingnor_FileExistsError:
            raise


def write_file(path: str, content: str, method: str = 'w') -> None:
    with open(path, method) as file:
        file.write(content)