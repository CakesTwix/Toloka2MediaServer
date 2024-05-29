"""Functions for working with torrents"""
import logging
import time

from toloka2MediaServer.clients.bittorrent_client import BittorrentClient

from toloka2MediaServer.config import toloka, app, selectedClient, update_config
from toloka2MediaServer.utils.title import Title, title_to_config
from toloka2MediaServer.utils.general import get_numbers, replace_second_part_in_path, get_folder_name_from_path

logger = logging.getLogger(__name__)

def process_torrent(client: BittorrentClient, torrent, title: Title, new=False):
    """ Common logic to process torrents, either updating or adding new ones """
    title.publish_date = torrent.date if new else torrent.registered_date
    
    tolokaTorrentFile = toloka.download_torrent(f"{toloka.toloka_url}/{torrent.download_link if new else torrent.torrent_url}")
        
    category = app[selectedClient]["category"]
    tag = app[selectedClient]["tag"]
    
    add_torrent_response = client.add_torrent(torrents=tolokaTorrentFile, category=category, tags=[tag], is_paused=True, download_dir=title.download_dir)
    time.sleep(2)
    if selectedClient == "qbittorrent":
        filtered_torrents = client.get_torrent_info(status_filter=['paused'], category=category, tags=[tag], sort="added_on", reverse=True, torrent_hash=None)
        added_torrent = filtered_torrents[0]
        title.hash = added_torrent.info.hash
        get_filelist = client.get_files(title.hash)

    else:
        added_torrent = client.get_torrent_info(status_filter=['paused'], category=category, tags=[tag], sort="added_on", reverse=True, torrent_hash=add_torrent_response)
        title.hash = added_torrent.id
        get_filelist = added_torrent.get_files()
        
    logger.debug(added_torrent)
    
    first_fileName = get_filelist[0].name

    if new:
        
        title.guid = torrent.url
        # Extract numbers from the filename
        numbers = get_numbers(first_fileName)
        
        if title.episode_index == -1:
            # Display the numbers to the user, starting count from 1
            print(f"{first_fileName}\nEnter the order number of the episode index from the list below:")
            for index, number in enumerate(numbers, start=1):
                print(f"{index}: {number}")

            # Get user input and adjust for 0-based index
            episode_order = int(input("Your choice (use order number): "))
            episode_index = episode_order - 1  # Convert to 0-based index
            source_episode_number = numbers[episode_index]
            print(f"You selected episode number: {numbers[episode_index]}")
        
            adjustment_input = input("Enter the adjustment value (e.g., '+9' or '-3', default is 0): ").strip()
            adjusted_episode_number = int(adjustment_input) if adjustment_input else 0
            
            if adjusted_episode_number != 0:
                # Calculate new episode number considering adjustment and preserve leading zeros if any
                adjusted_episode = str(int(source_episode_number) + adjusted_episode_number).zfill(len(source_episode_number))
            else:
                adjusted_episode = source_episode_number
            print(f"Adjusted episode number: {adjusted_episode}")
            
            title.episode_index = episode_index
            title.adjusted_episode_number = adjusted_episode_number
    
    for file in get_filelist:
        if title.ext_name not in file.name:
            continue
        
        source_episode = get_numbers(file.name)[title.episode_index]
        calculated_episode = str(int(source_episode) + title.adjusted_episode_number).zfill(len(source_episode))
        new_name = f"{title.torrent_name} S{title.season_number}E{calculated_episode} {title.meta}-{title.release_group}{title.ext_name}"
        if selectedClient == "qbittorrent":
            new_path = replace_second_part_in_path(file.name, new_name)
        else:
            new_path = new_name
        client.rename_file(torrent_hash=title.hash, old_path=file.name, new_path=new_path)

    folderName = f"{title.torrent_name} S{title.season_number} {title.meta}[{title.release_group}]"
    old_path = get_folder_name_from_path(first_fileName)
    client.rename_folder(torrent_hash=title.hash, old_path=old_path, new_path=folderName)
    client.rename_torrent(torrent_hash=title.hash, new_torrent_name=folderName)
    
    config = title_to_config(title)
    if new:
        client.resume_torrent(torrent_hashes=title.hash)
    else:
        client.recheck_torrent(torrent_hashes=title.hash)
        client.resume_torrent(torrent_hashes=title.hash)
        
    update_config(config, title.code_name)    
    #qbt_client.auth_log_out() logout from qbit session TBD
    
def update(client: BittorrentClient, title: Title, force: bool):
    torrent = toloka.get_torrent(f"{toloka.toloka_url}/{title.guid.strip('"')}")
    if title.publish_date not in torrent.registered_date:
        logger.info(f"Date is different! : {torrent.name}")
        if not force:
            client.delete_torrent(delete_files=False, torrent_hashes=title.hash)
        process_torrent(client, torrent, title)
    else:
        logger.info(f"Update not required! : {torrent.name}")

def add(client: BittorrentClient, torrent, title: Title):

    process_torrent(client, torrent, title=title, new=True)
    client.end_session()