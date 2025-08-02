from datetime import datetime
from functools import wraps
import os


def logger(path):
    def __logger(old_function):
        @wraps(old_function)
        def new_function(*args, **kwargs):
            datantime = datetime.now().strftime('%d.%m.%Y %H:%M')

            result = old_function(*args, **kwargs)
            log_line = (f'{datantime} - {old_function.__name__} - '
                        f'{args} - {kwargs} - {result}\n')
            
            method = 'a' if os.path.exists('main.log') else 'w'
            with open(path, method, encoding="utf-8") as f:
                f.write(log_line)

            return result
        return new_function
    return __logger