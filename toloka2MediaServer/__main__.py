"""Entering the program, this is where it all starts"""
import argparse
import logging
import sys
import re
import time
from toloka2MediaServer.config import app, titles, toloka

# Configure logging
# Yeah, I know, that it looks strange, but .basicConfig not working for some reason
# with manual handler add, it starts writing to a file.
config_level_name = app["Python"]["logging"]
# Use getattr to safely get the logging level from the logging module
# Default to logging.INFO if the specified level name is not found
logging_level = getattr(logging, config_level_name.upper(), logging.INFO)

logging.basicConfig(
    filename='toloka2MediaServer/data/app.log',  # Name of the file where logs will be written
    filemode='a',  # Append mode, which will append the logs to the file if it exists
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of the log messages
    level=logging_level #log level from config
)
logger = logging.getLogger(__name__)

logger.setLevel(logging_level)  # Set the logger to capture INFO and higher level messages
# Create a file handler which logs even debug messages
fh = logging.FileHandler('toloka2MediaServer/data/app.log')
fh.setLevel(logging_level)  # Set the file handler to capture DEBUG and higher level messages
# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(fh)

logger.info("------------------------------------------")

from toloka2MediaServer.clients.dynamic import dynamic_client_init
from toloka2MediaServer.utils.torrent_processor import add, update
from toloka2MediaServer.utils.title import Title, config_to_title
from toloka2MediaServer.utils.general import extract_torrent_details, get_numbers


# Initialize the client based on configuration
client = dynamic_client_init()

# Setup argparse
parser = argparse.ArgumentParser(description="Console utility for updating torrents from Toloka.")

# Create argument groups
main_group = parser.add_argument_group('Main Arguments')
add_group = parser.add_argument_group('Add Release Arguments')
util_group = parser.add_argument_group('Utility Arguments')

# Main Arguments
main_group.add_argument("-c", "--codename", type=str, help="Codename of the title", required=False)
main_group.add_argument("-a", "--add", nargs='?', const="default", help="Add new release to config", required=False)

# Utility Arguments
util_group.add_argument("-n", "--num", type=str, help="Get list of numbers from string", required=False)
util_group.add_argument("-f", "--force", action='store_true', help="Force download regardless of torrent presence", required=False)

# Add Release Arguments
add_group.add_argument("-u", "--url", type=str, help="Toloka URL to release", required=False)
add_group.add_argument("-s", "--season", type=str, help="Season number", required=False)
add_group.add_argument("-i", "--index", type=int, help="Series index", required=False)
add_group.add_argument("-co", "--correction", type=int, help="Adjusted series number", required=False)
add_group.add_argument("-t", "--title", type=str, help="Series name", required=False)

args = parser.parse_args()

# Output numbers if requested
if args.num:
    print(get_numbers(args.num))
    sys.exit()

if args.url:
    #--add --url https://toloka.to/t675888 --season 02 --index 2 --correction 0 --title "Tsukimichi -Moonlit Fantasy-"
    logger.debug(f"--add {args.add} --url {args.url} --season {args.season} --index{args.index} --correction{args.correction} --title{args.title}")
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
    sys.exit()

# Adding new title
if args.add:
    #--add "Tsuki ga Michibiku Isekai Douchuu (Season 2)"
    logger.debug(f"--add {args.add}")
    title = Title()
    
    torrent = toloka.search(args.add)
    if not torrent:
        logger.info(f"No results found. {args.add}")
        sys.exit()
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
    sys.exit()

# Update specific or all anime
if args.codename:
    logger.debug(f"--codename {args.codename}")
    title_from_config = config_to_title(titles, args.codename)
    update(client, title_from_config, args.force)
    client.end_session()
else:
    logger.debug(f"no args, update all")
    for config in titles.sections():
        #just to be sure, that we are not ddosing toloka, wait for 10s before each title update, as otherwise cloudflare may block our ip during some rush hrs
        #could be changed to some configuration, as not so required for small list
        time.sleep(10)
        title_from_config = config_to_title(titles, config)
        update(client, title_from_config, args.force)
        client.end_session()

sys.exit()