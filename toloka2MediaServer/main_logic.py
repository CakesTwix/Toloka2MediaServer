from datetime import datetime
import re
import time
from toloka2MediaServer.clients.dynamic import dynamic_client_init
from toloka2MediaServer.models.operation_result import OperationResult, OperationType, ResponseCode
from toloka2MediaServer.utils.general import extract_torrent_details
from toloka2MediaServer.utils.operation_decorator import operation_tracker
from toloka2MediaServer.utils.title import Title, config_to_title
from toloka2MediaServer.utils.torrent_processor import add, update

from toloka2MediaServer.config import titles, toloka, application_config, update_titles

client = dynamic_client_init()

@operation_tracker(OperationType.ADD_BY_URL)  
def add_release_by_url(args, logger, operation_result=None):
    title = Title()
    title.episode_index = args.index - 1
    title.adjusted_episode_number = args.correction
    proposed_url = args.url
    proposed_guid = f"t{re.search(r't(\d+)', proposed_url).group(1)}"
    torrent = toloka.get_torrent(f"{toloka.toloka_url}/{proposed_guid}")
    suggested_name, suggested_codename = extract_torrent_details(torrent.name)
    title.code_name = suggested_codename
    # Collect additional data
    season_number = args.season
    title.season_number = season_number.zfill(2)
    title.ext_name = ".mkv"
    default_download_dir = application_config.default_download_dir
    title.download_dir = default_download_dir
    title.torrent_name = args.title or suggested_name
    title.release_group = torrent.author
    default_meta = application_config.default_meta
    title.meta = default_meta
    operation_result = add(client, torrent, title, operation_result)

@operation_tracker(OperationType.ADD_BY_CODE)    
def add_release_by_name(args, logger, operation_result=None):
    title = Title()
    torrent = toloka.search(args.add)
    if not torrent:
        logger.info(f"No results found. {args.add}")
        return
    for index, item in enumerate(torrent[:10]):
        print(f"{index} : {item.name} - {item.url}")
    torrent = torrent[int(input("Enter the index of the desired torrent: "))]
    suggested_name, suggested_codename = extract_torrent_details(torrent.name)
    title.code_name = input(f"Default:{suggested_codename}. Enter the codename: ") or suggested_codename
    # Collect additional data
    season_number = input("Enter the season number: ")
    title.season_number = season_number.zfill(2)
    title.ext_name = input('Enter the file extension, e.g., ".mkv": ') or ".mkv"
    default_download_dir = application_config.default_download_dir
    title.download_dir = input(f"Default: {default_download_dir}:. Enter the download directory path.  ") or default_download_dir
    title.torrent_name = input(f"Default: {suggested_name}. Enter the directory name for the downloaded files: ") or suggested_name
    title.release_group = input("Enter the release group name, or it will default to the torrent's author: ") or torrent.author
    default_meta = application_config.default_meta
    title.meta = input(f"Default: {default_meta}. Enter additional metadata tags: ") or default_meta
    operation_result = add(client, torrent, title, operation_result)

@operation_tracker(OperationType.UPDATE_BY_CODE)      
def update_release_by_name(args, codename, logger, operation_result=None):
    operation_result = update_release(args, codename, logger, operation_result)

def update_release(args, codename, logger, operation_result):
    #update to be sure, that we always work with latest version of titles
    titles = update_titles()
    title_from_config = config_to_title(titles, codename)
    operation_result = update(client, title_from_config, args.force, operation_result)
    client.end_session()
    return operation_result

@operation_tracker(OperationType.UPDATE_ALL)   
def update_releases(args, logger, operation_result=None):
    for config in titles.sections():
    #just to be sure, that we are not ddosing toloka, wait for 10s before each title update, as otherwise cloudflare may block our ip during some rush hrs
    #could be changed to some configuration, as not so required for small list
        time.sleep(application_config.wait_time)
        update_release(args, config, logger, operation_result)
        

def search_torrents(args, logger, operation_result=None):
    torrents = toloka.search(args)
    
    return torrents

def get_torrent(args, logger, operation_result=None):
    torrent = toloka.get_torrent(f"{toloka.toloka_url}/{args}")
    
    return torrent