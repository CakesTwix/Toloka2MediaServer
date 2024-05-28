"""Here we work with config files and some toloka"""
import configparser
from toloka2python import Toloka

# Load configuration files
app, titles = configparser.ConfigParser(), configparser.ConfigParser()
app.read("toloka2MediaServer/data/app.ini")
titles.read("toloka2MediaServer/data/titles.ini")

# Initialize Toloka client
toloka = Toloka(app["Toloka"]["username"], app["Toloka"]["password"])
selectedClient = app["Toloka"]["client"]

def update_config(config, code_name):
    """Update configuration file when a new torrent is added."""
    config_file = configparser.ConfigParser()
    config_file.read("toloka2MediaServer/data/titles.ini")

    config_file[code_name] = config[code_name]

    with open("toloka2MediaServer/data/titles.ini", 'w') as ini:
        config_file.write(ini)