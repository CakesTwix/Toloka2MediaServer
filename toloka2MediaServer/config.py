"""Here we work with config files and some toloka"""
import os
import configparser
from toloka2python import Toloka

from toloka2MediaServer.models.application import config_to_app

def load_configurations(app_config_path=None, title_config_path=None):
    """Load configuration files with flexibility on path specification."""
    if app_config_path is None:
        app_config_path = os.path.join(os.getcwd(), 'data', 'app.ini')
    if title_config_path is None:
        title_config_path = os.path.join(os.getcwd(), 'data', 'titles.ini')

    app_config = configparser.ConfigParser()
    title_config = configparser.ConfigParser()
    app_config.read(app_config_path)
    title_config.read(title_config_path)
    return app_config, title_config

# Example usage of load_configurations
app_config, title_config = load_configurations()

application_config = config_to_app(app_config)

# Initialize Toloka client
toloka = Toloka(application_config.username, application_config.password)

def update_titles(title_config_path=None):
    """Update titles from the configuration file."""
    if title_config_path is None:
        title_config_path = os.path.join(os.getcwd(), 'data', 'titles.ini')
    titles = configparser.ConfigParser()
    titles.read(title_config_path)
    return titles

def update_config(config, code_name, title_config_path=None):
    """Update configuration file when a new torrent is added."""
    if title_config_path is None:
        title_config_path = os.path.join(os.getcwd(), 'data', 'titles.ini')
    config_file = configparser.ConfigParser()
    config_file.read(title_config_path)

    config_file[code_name] = config[code_name]

    with open(title_config_path, 'w') as ini:
        config_file.write(ini)