"""Functions for working with torrents"""
import logging
import time

from toloka2MediaServer.config import titles, toloka, app, selectedClient, update_config_onAdd, update_config_onUpdate
from toloka2MediaServer.clients.transmission import client
from toloka2MediaServer.utils.general import get_numbers, replace_second_part_in_path, get_folder_name_from_path

def process_torrent(torrent, config, force=False, new=False, codename=None, config_update=None):
    """ Common logic to process torrents, either updating or adding new ones """
    tolokaTorrentFile = toloka.download_torrent(f"{toloka.toloka_url}/{torrent.download_link if new else torrent.torrent_url}")
        
    category = app[selectedClient]["category"]
    tag = app[selectedClient]["tag"]
    #category=category, tags=[tag]
    torrent_hash = client.add_torrent(tolokaTorrentFile, download_dir=config["download_dir"], labels=[category,tag], paused=True).id
    added_torrent = client.get_torrent(torrent_hash)
    torrent_hash = added_torrent.id
    
    get_filelist = added_torrent.get_files()
    first_fileName = get_filelist[0].name 

    if new:
        # Extract numbers from the filename
        numbers = get_numbers(first_fileName)

        # Display the numbers to the user, starting count from 1
        print(f"{first_fileName}\nEnter the order number of the episode index from the list below:")
        for index, number in enumerate(numbers, start=1):
            print(f"{index}: {number}")

        # Get user input and adjust for 0-based index
        episode_order = int(input("Your choice (use order number): "))
        episode_index = episode_order - 1  # Convert to 0-based index
        episode_number = episode_index
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
    else:
        episode_number = int(config['episode_number'])
        adjusted_episode_number = int(config['adjusted_episode_number'])

    torrent_name = config['torrent_name'].strip('"')
    for file in get_filelist:
        if '.pad' in file.name or config['ext_name'] not in file.name:
            continue
        source_episode = get_numbers(file.name)[episode_number]
        calculated_episode = str(int(source_episode) + adjusted_episode_number).zfill(len(source_episode))
        new_name = f"{torrent_name} S{config['season_number']}E{calculated_episode} {config['meta']}-{config['release_group']}{config['ext_name']}"
        new_path = new_name #replace_second_part_in_path(file.name, new_name) 
        
        client.rename_torrent_path(torrent_id=torrent_hash, location=file.name, name=new_path)

    folderName = f"{torrent_name} S{config['season_number']} {config['meta']}[{config['release_group']}]"
    old_path = get_folder_name_from_path(first_fileName)
    
    client.rename_torrent_path(torrent_hash, old_path, folderName)
    #Torrent Rename and folder rename same action in transmission api.
    
    if new:
        client.start_torrent(torrent_hash)
        
        if selectedClient == 'Transmission':
            torrent_hash = str(torrent_hash)
        update_config_onAdd(config_update, torrent_hash, torrent.url, codename, episode_number, config['season_number'], config['ext_name'], config['torrent_name'], config['download_dir'], torrent.date, config['release_group'], config['meta'], adjusted_episode_number)
    else:
        client.verify_torrent(torrent_hash)
        client.start_torrent(torrent_hash)
        
        if selectedClient == 'Transmission':
            torrent_hash = str(torrent_hash)
        update_config_onUpdate(config, torrent.registered_date, torrent_hash)

    
def update(title: str, force: bool):
    config_title = titles[title]
    torrent = toloka.get_torrent(f"{toloka.toloka_url}/{config_title['guid'].strip('"')}")
    if config_title["PublishDate"] not in torrent.registered_date:
        logging.info(f"Date is different! : {torrent.name}")
        if not force:
            client.remove_torrent(config_title["hash"])
        process_torrent(torrent, config_title, force=force)

def add(torrent, codename, config_update, season_number, ext_name, download_dir, torrent_name, release_group, meta):
    config = {
        "season_number": season_number,
        "ext_name": ext_name,
        "torrent_name": torrent_name,
        "release_group": release_group,
        "meta": meta,
        "download_dir": download_dir
    }
    process_torrent(torrent, config, new=True, codename=codename, config_update=config_update)