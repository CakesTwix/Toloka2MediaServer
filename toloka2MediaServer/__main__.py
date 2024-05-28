"""Entering the program, this is where it all starts"""
import argparse
import logging
import sys
import re
import time

from toloka2MediaServer.config import app, titles, toloka, selectedClient
# Configure logging
logging.basicConfig(level=app["Python"]["logging"])

# Dynamic client import based on selected client
client_module = f"toloka2MediaServer.clients.{selectedClient.lower()}"
utils_module = f"toloka2MediaServer.utils.{selectedClient.lower()}"
client = __import__(client_module, fromlist=['client']).client
update = __import__(utils_module, fromlist=['update']).update
add = __import__(utils_module, fromlist=['add']).add

from toloka2MediaServer.utils.title import Title, config_to_title
from toloka2MediaServer.utils.general import extract_torrent_details, get_numbers

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
    
    add(torrent, title)
    sys.exit()

# Adding new title
if args.add:
    #--add "Tsuki ga Michibiku Isekai Douchuu (Season 2)"
    title = Title()
    
    torrent = toloka.search(args.add)
    if not torrent:
        logging.info("No results found.")
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

    add(torrent, title)
    sys.exit()

# Update specific or all anime
if args.codename:
    update(args.codename, args.force)
else:
    for title in titles.sections():
        #just to be sure, that we are not ddosing toloka, wait for 10s before each call.
        time.sleep(10)
        title = config_to_title(titles, title)
        update(title, args.force)