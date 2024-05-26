"""Functions for working with torrents"""
import logging

from toloka2anime.config import titles, toloka, app, selectedClient, update_config_onAdd, update_config_onUpdate
from toloka2anime.clients.qbittorrent import client
from toloka2anime.utils.general import get_numbers, replace_second_part_in_path, get_folder_name_from_path

def process_torrent(torrent, config, force=False, new=False, codename=None, config_update=None):
    """ Common logic to process torrents, either updating or adding new ones """
    tolokaTorrentFile = toloka.download_torrent(f"{toloka.toloka_url}/{torrent.download_link}")
    client.torrents.add(torrent_files=tolokaTorrentFile, category=config["category"], tags=[config["tag"]], is_paused=True)
    added_torrent = client.torrents_info(status_filter=['paused'], category=config["category"], tags=[config["tag"]], sort="added_on")
    torrent_hash = added_torrent[0]['hash']
    added_torrent = client.torrents.properties(torrent_hash)
    logging.debug(added_torrent)
    get_filelist = client.torrents.files(torrent_hash)
    first_fileName = get_filelist[0].name

    if new:
        episode_number = int(input(f"Enter episode index\n{first_fileName} : {get_numbers(first_fileName)}: "))
    else:
        episode_number = config['episode_number']

    for file in get_filelist:
        new_name = f"{config['torrent_name']} S{config['season_number']}E{get_numbers(file.name)[episode_number]} {config['meta']}-{config['release_group']}{config['ext_name']}"
        new_path = replace_second_part_in_path(file.name, new_name)
        client.torrents.rename_file(torrent_hash=torrent_hash, old_path=file.name, new_path=new_path)

    folderName = f"{config['torrent_name']} S{config['season_number']} {config['meta']}[{config['release_group']}]"
    old_path = get_folder_name_from_path(first_fileName)
    client.torrents.rename_folder(torrent_hash=torrent_hash, old_path=old_path, new_path=folderName)
    client.torrents.rename(torrent_hash=torrent_hash, new_torrent_name=config['torrent_name'])
    client.torrents.resume(torrent_hashes=torrent_hash)

    if new:
        update_config_onAdd(config_update, torrent_hash, codename, episode_number, config['season_number'], config['ext_name'], config['torrent_name'], config['download_dir'], torrent.date, config['release_group'], config['meta'])
    else:
        update_config_onUpdate(config, torrent.registered_date, torrent_hash)

def update(title: str, force: bool):
    config_title = titles[title]
    torrent = toloka.get_torrent(f"{toloka.toloka_url}/{config_title['guid']}")
    if config_title["PublishDate"] not in torrent.registered_date:
        logging.info(f"Date is different! : {torrent.name}")
        if not force:
            client.torrents_delete(delete_files=False, torrent_hashes=config_title["hash"])
        process_torrent(torrent, config_title, force=force)

def add(torrent, codename, config_update, season_number, ext_name, download_dir, torrent_name, release_group, meta):
    config = {
        "category": app[selectedClient]["category"],
        "tag": app[selectedClient]["tag"],
        "season_number": season_number,
        "ext_name": ext_name,
        "torrent_name": torrent_name,
        "release_group": release_group,
        "meta": meta,
        "download_dir": download_dir
    }
    process_torrent(torrent, config, new=True, codename=codename, config_update=config_update)