"""Here we work with config files and some toloka"""
import os
import configparser
from toloka2python import Toloka

def load_configurations(app_config_path=None, title_config_path=None):
    """Load configuration files with flexibility on path specification."""
    if app_config_path is None:
        app_config_path = os.path.join(os.getcwd(), 'data', 'app.ini')
    if title_config_path is None:
        title_config_path = os.path.join(os.getcwd(), 'data', 'titles.ini')

    app_config = configparser.ConfigParser()
    titles_config = configparser.ConfigParser()
    app_config.read(app_config_path)
    titles_config.read(title_config_path)
    return app_config, titles_config

def get_toloka_client(application_config):
    return Toloka(application_config.username, application_config.password)

def update_config(config, code_name, title_config_path=None):
    """Update configuration file when a new torrent is added."""
    if title_config_path is None:
        title_config_path = os.path.join(os.getcwd(), 'data', 'titles.ini')
    config_file = configparser.ConfigParser()
    config_file.read(title_config_path)

    config_file[code_name] = config[code_name]

    with open(title_config_path, 'w') as ini:
        config_file.write(ini)