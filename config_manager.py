import configparser


class ConfigManager:
    def __init__(self, filepath='settings.ini'):
        self.config = configparser.ConfigParser()
        self.filepath = filepath

    def load_config(self):
        self.config.read(self.filepath)
        defaults = {'ServerIP': '127.0.0.1',
                    'ServerPort': '9999',
                    'SerialPort': 'COM1',
                    'BaudRate': '9600',
                    'PrintLog': 'False',
                    'HexLog': 'False',
                    'EnableHeartbeat': 'False',
                    'HeartbeatData': '',
                    'HeartbeatInterval': '0',
                    'HeartbeatHex':'False',
                    'AutoReconnect':'True'
                    }
        for key, value in defaults.items():
            if key not in self.config['DEFAULT']:
                self.config['DEFAULT'][key] = value
        self.save_config()

    def save_config(self):
        with open(self.filepath, 'w') as configfile:
            self.config.write(configfile)

    def get_config(self):
        return self.config['DEFAULT']

    def update_config(self, **kwargs):
        for key, value in kwargs.items():
            self.config['DEFAULT'][key] = value
        self.save_config()
