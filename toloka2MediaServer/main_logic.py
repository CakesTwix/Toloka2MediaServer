import re
import time
from toloka2MediaServer.clients.dynamic import dynamic_client_init
from toloka2MediaServer.utils.general import extract_torrent_details
from toloka2MediaServer.utils.title import Title, config_to_title
from toloka2MediaServer.utils.torrent_processor import add, update

from toloka2MediaServer.config import app, titles, toloka

client = dynamic_client_init()

def add_release_by_url(args, logger):
    title = Title()
    title.episode_index = args.index
    title.adjusted_episode_number = args.correction
    
    proposed_url = args.url
    proposed_guid = f"t{re.search(r't(\d+)', proposed_url).group(1)}"
    torrent = toloka.get_torrent(f"{toloka.toloka_url}/{proposed_guid}")
    
    #temporary fix, as get_torrent returns other fields
    search_torrent = toloka.search(torrent.name)
    matched_index = 0
    for index, item in enumerate(search_torrent[:10]):
        matched_index = index if item.url == proposed_guid else 0
    torrent = search_torrent[matched_index]
    suggested_name, suggested_codename = extract_torrent_details(torrent.name)

    title.code_name = suggested_codename
    
    # Collect additional data
    season_number = args.season
    title.season_number = season_number.zfill(2)
    title.ext_name = ".mkv"
    default_download_dir = app["Toloka"]["default_download_dir"]
    title.download_dir = default_download_dir
    title.torrent_name = args.title or suggested_name
    title.release_group = torrent.author
    default_meta = app["Toloka"]["default_meta"]
    title.meta = default_meta
    
    add(client, torrent, title)
    
def add_release_by_name(args, logger):
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
    default_download_dir = app["Toloka"]["default_download_dir"]
    title.download_dir = input(f"Default: {default_download_dir}:. Enter the download directory path.  ") or default_download_dir
    title.torrent_name = input(f"Default: {suggested_name}. Enter the directory name for the downloaded files: ") or suggested_name
    title.release_group = input("Enter the release group name, or it will default to the torrent's author: ") or torrent.author
    default_meta = app["Toloka"]["default_meta"]
    title.meta = input(f"Default: {default_meta}. Enter additional metadata tags: ") or default_meta

    add(client, torrent, title)
    
def update_release_by_name(args, codename, logger):
    title_from_config = config_to_title(titles, codename)
    update(client, title_from_config, args.force)
    client.end_session()

def update_releases(args, logger):
    for config in titles.sections():
        #just to be sure, that we are not ddosing toloka, wait for 10s before each title update, as otherwise cloudflare may block our ip during some rush hrs
        #could be changed to some configuration, as not so required for small list
        time.sleep(10)
        update_release_by_name(args, config, logger)