"""Functions for working with torrents"""
import logging

from toloka2anime.config import titles, toloka, app, selectedClient
from toloka2anime.clients.qbit import client
from toloka2anime.utils.general import get_numbers


def update(title: str, force: bool):
    # All ok, do magic ^_^
    # Search Anime by "search query" and check Guid
    torrent_toloka = toloka.get_torrent(f"{toloka.toloka_url}/{titles[title]['guid']}")

    # Check if have updates by date
    if titles[title]["PublishDate"] in torrent_toloka.registered_date:
        logging.info(f"Same date! : {torrent_toloka.name}")
        return
    else:
        # We have some changes! Do redownload torrent
        logging.info(f"Date is different! : {torrent_toloka.name}")

    # Get all torrents and get one by name
    for torrent in client.get_torrents():
        if titles[title]["torrent_name"] == torrent.name or force:
            # Remove old torrent
            if force != True:
                client.remove_torrent(torrent.id)
                
            # Download torrent file
            new_torrent = client.get_torrent(
                client.add_torrent(
                    toloka.download_torrent(f"{toloka.toloka_url}/{torrent_toloka.torrent_url}"),
                    download_dir=titles[title]["download_dir"],
                ).id
            )

            # Rename episodes
            if titles[title]["episode_number"]:
                # New torrent Files
                for name in new_torrent.get_files():
                    # Episode S1E01.mkv
                    new_name = f"{titles[title]['torrent_name']} S{titles[title]['season_number']}E{get_numbers(name.name)[int(titles[title]['episode_number'])]}{titles[title]['ext_name']}".replace(" ", ".")
                    client.rename_torrent_path(
                        new_torrent.id, name.name, new_name
                    )

            # Rename Torrent
            client.rename_torrent_path(
                new_torrent.id,
                new_torrent.name,
                titles[title]["torrent_name"],
            )

            # Check old files
            client.verify_torrent(new_torrent.id)
            client.start_torrent(new_torrent.id)

            # Update date and write
            titles[title]["PublishDate"] = torrent_toloka.registered_date
            with open("titles.ini", "w", encoding="utf-8") as conf:
                titles.write(conf)

            # No need check next torrents
            break

def replace_second_part_in_path(path, name):
    parts = path.split("/")
    if len(parts) > 1:
        parts[1] = name
    return "/".join(parts)

def get_folder_name_from_path(path):
    parts = path.split("/")
    if len(parts) > 1:
        return parts[0]
    return ""

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

    # Write data
    config_update.set(codename, "episode_number", episode_number)
    config_update.set(codename, "season_number", season_number)
    config_update.set(codename, "ext_name", ext_name)
    config_update.set(codename, "torrent_name", torrent_name)
    config_update.set(codename, "download_dir", download_dir)
    config_update.set(codename, "publishdate", torrent.date)
    config_update.set(codename, "release_group", release_group)
    config_update.set(codename, "meta", meta)

    # Write to config
    with open("titles.ini", "a", encoding="utf-8") as f:
        config_update.write(f)
