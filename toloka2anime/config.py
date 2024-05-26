"""Here we work with config files and some toloka"""
import configparser
from toloka2python import Toloka

app, titles = configparser.ConfigParser(), configparser.ConfigParser()
app.read("toloka2anime/data/app.ini")
titles.read("toloka2anime/data/titles.ini")

toloka = Toloka(app["Toloka"]["username"], app["Toloka"]["password"])
selectedClient = app["Toloka"]["client"]

def update_config_onAdd(config_update, torrent_hash, codename, episode_number ,season_number ,ext_name , torrent_name, download_dir, date, release_group, meta):
    # Write data
    config_update.set(codename, "episode_number", episode_number)
    config_update.set(codename, "season_number", season_number)
    config_update.set(codename, "ext_name", ext_name)
    config_update.set(codename, "torrent_name", torrent_name)
    config_update.set(codename, "download_dir", download_dir)
    config_update.set(codename, "publishdate", date)
    config_update.set(codename, "release_group", release_group)
    config_update.set(codename, "meta", meta)
    config_update.set(codename, "hash", torrent_hash)

    # Write to config
    with open("toloka2anime/data/titles.ini", "a", encoding="utf-8") as f:
        config_update.write(f)
        
def update_config_onUpdate(config_title, registered_date, torrent_hash):
    # Update date and write
    config_title["PublishDate"] = registered_date
    config_title["hash"] = torrent_hash
    
    with open("titles.ini", "w", encoding="utf-8") as conf:
        titles.write(conf)