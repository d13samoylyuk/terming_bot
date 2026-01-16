from modules.files import read_json_file, save_json_file


'''
Program paths
'''
class PATHS:
    dict = 'data/rus_eng_dict.csv'
    log = 'data/main.log'
    errors_terms = 'data/errors_dict.json'
    env = 'data/.env'
    configs = 'config/config.json'


'''
Program configs
'''
class CONFIGS:
    def __init__(self):
        self._configs = self._get_configs()

        # Shows users who switched to only their terms
        self.switched_mode = self._configs['switched_mode']

    def switch_user_mode(self, user_id):
        if user_id in self.switched_mode:
            self.switched_mode.remove(user_id)
            self._update_configs()
            return 'full'
        else:
            self.switched_mode.append(user_id)
            self._update_configs()
            return 'self'
    
    def current_mode(self, user_id):
        if user_id in self.switched_mode:
            return 'self'
        else:
            return 'full'

    def _get_configs(self):
        return read_json_file(PATHS.configs)
    
    def _update_configs(self):
        save_json_file(self._configs, PATHS.configs)
    
    def __str__(self):
        return str(self._configs)