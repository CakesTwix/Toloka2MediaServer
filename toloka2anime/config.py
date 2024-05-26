"""Here we work with config files and some toloka"""
import configparser
from toloka2python import Toloka

# Load configuration files
app, titles = configparser.ConfigParser(), configparser.ConfigParser()
app.read("toloka2anime/data/app.ini")
titles.read("toloka2anime/data/titles.ini")

# Initialize Toloka client
toloka = Toloka(app["Toloka"]["username"], app["Toloka"]["password"])
selectedClient = app["Toloka"]["client"]

def update_config_onAdd(config_update, torrent_hash, torrent_guid, codename, episode_number, season_number, ext_name, torrent_name, download_dir, date, release_group, meta, adjusted_episode_number):
    """Update configuration file when a new torrent is added."""
    config_update.read("toloka2anime/data/titles.ini", encoding="utf-8")
    
    config_update[codename] = {
        "episode_number": str(episode_number),
        "season_number": str(season_number),
        "ext_name": ext_name,
        "torrent_name": f'"{torrent_name}"',
        "download_dir": download_dir,
        "publishdate": date,
        "release_group": release_group,
        "meta": meta,
        "hash": torrent_hash,
        "adjusted_episode_number": adjusted_episode_number,
        "guid": f'"{torrent_guid}"'
    }
    with open("toloka2anime/data/titles.ini", "w", encoding="utf-8") as f:
        config_update.write(f)

def update_config_onUpdate(config_title, registered_date, torrent_hash):
    """Update configuration file when an existing torrent is updated."""
    titles[config_title.name]["PublishDate"] = registered_date
    titles[config_title.name]["hash"] = torrent_hash
    with open("toloka2anime/data/titles.ini", "w", encoding="utf-8") as conf:
        titles.write(conf)