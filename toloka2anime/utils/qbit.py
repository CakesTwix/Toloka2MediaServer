"""Functions for working with torrents"""
import logging

from toloka2anime.config import titles, toloka, app, selectedClient, update_config_onAdd, update_config_onUpdate
from toloka2anime.clients.qbit import client
from toloka2anime.utils.general import get_numbers, replace_second_part_in_path, get_folder_name_from_path



def update(title: str, force: bool):
    config_title = titles[title]
    torrent_name = config_title['torrent_name']
    season_number = config_title['season_number']
    episode_number = config_title['episode_number']
    meta = config_title['meta']
    release_group = config_title['release_group']
    ext_name = config_title['ext_name']
    
    # Search Anime by "search query" and check Guid
    torrent = toloka.get_torrent(f"{toloka.toloka_url}/{config_title['guid']}")

    # Check if have updates by date
    if config_title["PublishDate"] in torrent.registered_date:
        logging.info(f"Same date! : {torrent.name}")
        return
    else:
        # We have some changes! Do redownload torrent
        logging.info(f"Date is different! : {torrent.name}")

    # Remove old torrent but keep files
    if force != True:
        client.torrents_delete(delete_files=False, torrent_hashes=config_title["hash"])
    
        #download torrent from toloka
    tolokaTorrentFile = toloka.download_torrent(f"{toloka.toloka_url}/{torrent.download_link}")
    #add torrent to qbit with cat and tag
    client.torrents.add(torrent_files=tolokaTorrentFile, category=config_title["category"], tags=[config_title["tag"]], is_paused = True)
    #torrent add returns status only, so we need to get hash of the torrent manually
    added_torrent = client.torrents_info(status_filter=['paused'],category=config_title["category"], tags=[config_title["tag"]], sort="added_on")
    torrent_hash = added_torrent[0]['hash']

    #validate torrent info and state
    added_torrent = client.torrents.properties(torrent_hash)
    logging.debug(added_torrent)
    
    get_filelist = client.torrents.files(torrent_hash)
    first_fileName = get_filelist[0].name
    
    #rename torrent files to format
    for file in get_filelist:
        # Episode S1E01.mkv
        new_name = f"{torrent_name} S{season_number}E{get_numbers(file.name)[episode_number]} {meta}-{release_group}{ext_name}"
        new_path = replace_second_part_in_path(file.name, new_name)
        client.torrents.rename_file(torrent_hash = torrent_hash, old_path = file.name, new_path = new_path)

    # Rename Torrent folder
    folderName = f"{torrent_name} S{season_number} {meta}[{release_group}]"
    old_path = get_folder_name_from_path(first_fileName)
    client.torrents.rename_folder(torrent_hash=torrent_hash, old_path=old_path, new_path=folderName)
    # Rename Torrent itself
    client.torrents.rename(torrent_hash=torrent_hash, new_torrent_name=torrent_name)
    
        # Check old files
    client.torrents.recheck(torrent_hashes=torrent_hash)
    client.torrents.resume(torrent_hashes=torrent_hash)
    
    update_config_onUpdate(config_title, torrent.registered_date, torrent_hash)

# Add new anime to titles.ini
def add(torrent, codename, config_update, season_number, ext_name, download_dir, torrent_name, release_group, meta):
    
    #download torrent from toloka
    tolokaTorrentFile = toloka.download_torrent(f"{toloka.toloka_url}/{torrent.download_link}")
    #add torrent to qbit with cat and tag
    client.torrents.add(torrent_files=tolokaTorrentFile, category=app[selectedClient]["category"], tags=[app[selectedClient]["tag"]], is_paused = True)
    #torrent add returns status only, so we need to get hash of the torrent manually
    added_torrent = client.torrents_info(status_filter=['paused'],category=app[selectedClient]["category"], tags=[app[selectedClient]["tag"]], sort="added_on")
    torrent_hash = added_torrent[0]['hash']

    #validate torrent info and state
    added_torrent = client.torrents.properties(torrent_hash)
    logging.debug(added_torrent)
    
    get_filelist = client.torrents.files(torrent_hash)
    first_fileName = get_filelist[0].name
    

    episode_number = int(
        input(
            f"Введіть індекс серії\n{first_fileName} : {get_numbers(first_fileName)}: "
        )
    )
    
    #TBD check path, error here?
    #rename torrent files to format
    for file in get_filelist:
        # Episode S1E01.mkv
        new_name = f"{torrent_name} S{season_number}E{get_numbers(file.name)[episode_number]} {meta}-{release_group}{ext_name}"
        new_path = replace_second_part_in_path(file.name, new_name)
        client.torrents.rename_file(torrent_hash = torrent_hash, old_path = file.name, new_path = new_path)

    # Rename Torrent folder
    folderName = f"{torrent_name} S{season_number} {meta}[{release_group}]"
    old_path = get_folder_name_from_path(first_fileName)
    client.torrents.rename_folder(torrent_hash=torrent_hash, old_path=old_path, new_path=folderName)
    # Rename Torrent itself
    client.torrents.rename(torrent_hash=torrent_hash, new_torrent_name=torrent_name)

    # Start
    client.torrents.resume(torrent_hashes=torrent_hash)

    # Write data to config
    update_config_onAdd(config_update, torrent_hash, codename, episode_number ,season_number ,ext_name , torrent_name, download_dir, torrent.date, release_group, meta)