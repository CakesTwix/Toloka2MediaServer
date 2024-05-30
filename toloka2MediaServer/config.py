"""Here we work with config files and some toloka"""
import configparser
from toloka2python import Toloka

path_to_app_config = "toloka2MediaServer/data/app.ini"
path_to_title_config = "toloka2MediaServer/data/titles.ini"

# Load configuration files
app, titles = configparser.ConfigParser(), configparser.ConfigParser()
app.read(path_to_app_config)
titles.read(path_to_title_config)

def update_titles():
    titles = configparser.ConfigParser()
    titles.read(path_to_title_config)
    return titles

# Initialize Toloka client
toloka = Toloka(app["Toloka"]["username"], app["Toloka"]["password"])
selectedClient = app["Toloka"]["client"]

def update_config(config, code_name):
    """Update configuration file when a new torrent is added."""
    config_file = configparser.ConfigParser()
    config_file.read(path_to_title_config)

    config_file[code_name] = config[code_name]

    with open(path_to_title_config, 'w') as ini:
        config_file.write(ini)