"""Functions for working with torrents"""
import logging
import time

from toloka2MediaServer.config import toloka, app, selectedClient, update_config
from toloka2MediaServer.clients.qbittorrent import client
from toloka2MediaServer.utils.title import Title, title_to_config
from toloka2MediaServer.utils.general import get_numbers, replace_second_part_in_path, get_folder_name_from_path

def process_torrent(torrent, title: Title, new=False):
    """ Common logic to process torrents, either updating or adding new ones """
    tolokaTorrentFile = toloka.download_torrent(f"{toloka.toloka_url}/{torrent.download_link if new else torrent.torrent_url}")
        
    category = app[selectedClient]["category"]
    tag = app[selectedClient]["tag"]
    
    #qbit api will not return hash of added torrent, so we are not able to make easy search request afterwards 
    client.torrents.add(torrent_files=tolokaTorrentFile, category=category, tags=[tag], is_paused=True)
    # Small timeout, as looks like sometimes it take a bit more time for qBit to add torrent(based on torrent size?)
    time.sleep(2)
    filtered_torrents = client.torrents_info(status_filter=['paused'], category=category, tags=[tag], sort="added_on", reverse=True)
    added_torrent = filtered_torrents[0]
    logging.debug(added_torrent)
    
    title.hash = added_torrent.info.hash
    title.publish_date = torrent.date if new else torrent.registered_date
    
    get_filelist = client.torrents.files(title.hash)
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
        source_episode = get_numbers(file.name)[title.episode_index]
        calculated_episode = str(int(source_episode) + title.adjusted_episode_number).zfill(len(source_episode))
        new_name = f"{title.torrent_name} S{title.season_number}E{calculated_episode} {title.meta}-{title.release_group}{title.ext_name}"
        new_path = replace_second_part_in_path(file.name, new_name)
        client.torrents.rename_file(torrent_hash=title.hash, old_path=file.name, new_path=new_path)

    folderName = f"{title.torrent_name} S{title.season_number} {title.meta}[{title.release_group}]"
    old_path = get_folder_name_from_path(first_fileName)
    client.torrents.rename_folder(torrent_hash=title.hash, old_path=old_path, new_path=folderName)
    client.torrents.rename(torrent_hash=title.hash, new_torrent_name=folderName)
    
    config = title_to_config(title)
    if new:
        client.torrents.resume(torrent_hashes=title.hash)
    else:
        #recheck not working? api bug?
        #client.torrents.recheck(torrent_hashes=torrent_hash) same added_torrent.recheck() do nothing
        added_torrent.recheck()
        client.torrents.resume(torrent_hashes=title.hash)
        
    update_config(config, title.code_name)    
    #qbt_client.auth_log_out() logout from qbit session TBD
    
def update(title: Title, force: bool):
    torrent = toloka.get_torrent(f"{toloka.toloka_url}/{title.guid.strip('"')}")
    if title.publish_date not in torrent.registered_date:
        logging.info(f"Date is different! : {torrent.name}")
        if not force:
            client.torrents_delete(delete_files=False, torrent_hashes=title.hash)
        process_torrent(torrent, title)
    else:
        logging.info(f"Update not required! : {torrent.name}")

def add(torrent, title: Title):

    process_torrent(torrent, title=title, new=True)