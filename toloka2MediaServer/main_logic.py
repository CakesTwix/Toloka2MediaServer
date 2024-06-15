from datetime import datetime
import re
import time
from toloka2MediaServer.models.operation_result import OperationResult, OperationType, ResponseCode
from toloka2MediaServer.utils.general import extract_torrent_details
from toloka2MediaServer.utils.operation_decorator import operation_tracker
from toloka2MediaServer.models.title import Title, config_to_title
from toloka2MediaServer.utils.torrent_processor import add, update

@operation_tracker(OperationType.ADD_BY_URL)  
def add_release_by_url(config):
    title = Title()
    title.episode_index = config.args.index - 1
    title.adjusted_episode_number = config.args.correction
    proposed_url = config.args.url
    proposed_guid = f"t{re.search(r't(\d+)', proposed_url).group(1)}"
    torrent = config.toloka.get_torrent(f"{config.toloka.toloka_url}/{proposed_guid}")
    suggested_name, suggested_codename = extract_torrent_details(torrent.name)
    title.code_name = suggested_codename
    # Collect additional data
    season_number = config.args.season
    title.season_number = season_number.zfill(2)
    title.ext_name = ".mkv"
    default_download_dir = config.application_config.default_download_dir
    title.download_dir = default_download_dir
    title.torrent_name = config.args.title.strip() or suggested_name.strip()
    title.release_group = torrent.author
    default_meta = config.application_config.default_meta
    title.meta = default_meta
    config.operation_result = add(config, title, torrent)
    
    return config.operation_result

@operation_tracker(OperationType.ADD_BY_CODE)    
def add_release_by_name(config):
    title = Title()
    torrent = config.toloka.search(config.args.add)
    if not torrent:
        message = f"No results found. {config.args.add}"
        config.logger.info(message)
        config.operation_result.response = message
        return config.operation_result
    for index, item in enumerate(torrent[:10]):
        print(f"{index} : {item.name} - {item.url}")
    torrent = torrent[int(input("Enter the index of the desired torrent: "))]
    suggested_name, suggested_codename = extract_torrent_details(torrent.name)
    title.code_name = input(f"Default:{suggested_codename}. Enter the codename: ") or suggested_codename
    # Collect additional data
    season_number = input("Enter the season number: ")
    title.season_number = season_number.zfill(2)
    title.ext_name = input('Enter the file extension, e.g., ".mkv": ') or ".mkv"
    default_download_dir = config.application_config.default_download_dir
    title.download_dir = input(f"Default: {default_download_dir}:. Enter the download directory path.  ") or default_download_dir
    title.torrent_name = input(f"Default: {suggested_name}. Enter the directory name for the downloaded files: ") or suggested_name
    title.release_group = input("Enter the release group name, or it will default to the torrent's author: ") or torrent.author
    default_meta = config.application_config.default_meta
    title.meta = input(f"Default: {default_meta}. Enter additional metadata tags: ") or default_meta
    config.operation_result = add(config, title, torrent)
    
    return config.operation_result

@operation_tracker(OperationType.UPDATE_BY_CODE)      
def update_release_by_name(config):
    config.operation_result = update_release(config)
    config.client.end_session()
    
    return config.operation_result

@operation_tracker(OperationType.UPDATE_ALL)   
def update_releases(config):
    for section in config.titles_config.sections():
    #just to be sure, that we are not ddosing toloka, wait for 10s(or what you have in config) before each title update, as otherwise cloudflare may block our ip during some rush hrs
        time.sleep(config.application_config.wait_time)
        config.args.codename = section
        config.operation_result = update_release(config)
    config.client.end_session()
    
    return config.operation_result

def update_release(config):
    """
    Updates release by provided name of the title. name extracted from args.codename

    Args:
        config (Config): A configuration object containing all necessary parameters like logger, client, etc.

    Returns:
        operation_result
    """
    title = config_to_title(config.titles_config, config.args.codename)
    config.operation_result = update(config, title)
    
    return config.operation_result

@operation_tracker(OperationType.SEARCH_RELEASES)  
def search_torrents(config):
    try:
        torrent = config.toloka.search(config.args)
        
        if not torrent:
            torrent = f"No results found. {config.args.add}"
        config.operation_result.response = torrent
    except Exception as e: 
        config.operation_result.response = e
        
    return config.operation_result

@operation_tracker(OperationType.GET_RELEASE)  
def get_torrent(config):
    try:
        torrent = config.toloka.get_torrent(f"{config.toloka.toloka_url}/{config.args}")
        
        if not torrent:
            torrent = f"No results found."
        config.operation_result.response = torrent
    except Exception as e: 
        config.operation_result.response = e
        
    return config.operation_result

@operation_tracker(OperationType.ADD_TORRENT)  
def add_torrent(config):
    try:
        if not config.args:
            config.operation_result.response = "No args provided"
            return config.operation_result
        torrent = config.toloka.download_torrent(f"{config.toloka.toloka_url}/{config.args.url}")
        
        # Safely get category and tags from config.args, default to empty string if None
        category = getattr(config.args, 'category', '') if config.args else ''
        tags = getattr(config.args, 'tags', '') if config.args else ''
        download_dir = getattr(config.args, 'download_dir', '') if config.args else ''
        config.client.add_torrent(torrents=torrent, category=category, tags=tags, is_paused=False, download_dir=download_dir)
        
        if not torrent:
            torrent = f"No results found."
        config.operation_result.response = torrent
    except Exception as e: 
        config.operation_result.response = e
        
    return config.operation_result