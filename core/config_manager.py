# core/config_manager.py
import configparser
import os
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            self.config['SETTINGS'] = {
                'language': 'english',
                'theme': 'light',
                'save_preview_files': 'False',
                'keep_transparent_color': 'False',
                'keep_temp_files': 'False'
            }
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
    
    def get(self, section, key, default=None):
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    
    def getboolean(self, section, key, default=False):
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = str(value)
        self.save_config()
