"""Entering the program, this is where it all starts"""
import argparse
import configparser
import logging
import sys
from toloka2anime.config import app, titles, toloka, selectedClient

# Dynamic client import based on selected client
client_module = f"toloka2anime.clients.{selectedClient.lower()}"
utils_module = f"toloka2anime.utils.{selectedClient.lower()}"
client = __import__(client_module, fromlist=['client']).client
update = __import__(utils_module, fromlist=['update']).update
add = __import__(utils_module, fromlist=['add']).add

from toloka2anime.utils.general import get_numbers

# Setup argparse
parser = argparse.ArgumentParser(description="Console utility for updating torrents from Toloka.")
parser.add_argument("-c", "--codename", type=str, help="Codename of the title")
parser.add_argument("-n", "--num", type=str, help="Get list of numbers from string")
parser.add_argument("-a", "--add", type=str, help="Add new anime to config.")
parser.add_argument("-f", "--force", action=argparse.BooleanOptionalAction, help="Force download regardless of torrent presence.")
args = parser.parse_args()

# Output numbers if requested
if args.num:
    print(get_numbers(args.num))
    sys.exit()

# Configure logging
logging.basicConfig(level=app["Python"]["logging"])

# Adding new anime
if args.add:
    torrent = toloka.search(args.add)
    if not torrent:
        logging.info("No results found.")
        sys.exit()

    for index, item in enumerate(torrent[:10]):
        print(f"{index} : {item.name} - {item.url}")

    torrent = torrent[int(input("Enter the index of the desired torrent: "))]
    codename = input("Enter the codename: ")
    config_update = configparser.RawConfigParser()
    config_update.add_section(codename)
    config_update.set(codename, "Guid", torrent.url)

    # Collect additional data
    season_number = input("Enter the season number: ")
    ext_name = input('Enter the file extension, e.g., ".mkv": ') or ".mkv"
    download_dir = input("Enter the download directory path: ")
    torrent_name = input("Enter the directory name for the downloaded files: ")
    release_group = input("Enter the release group name, or it will default to the torrent's author: ") or torrent.author
    meta = input("Enter additional metadata tags, or it will default to [WEBRip-1080p][UK+JA]: ") or "[WEBRip-1080p][UK+JA]"

    add(torrent, codename, config_update, season_number, ext_name, download_dir, torrent_name, release_group, meta)
    sys.exit()

# Update specific or all anime
if args.codename:
    update(args.codename, args.force)
else:
    for title in titles.sections():
        update(title, args.force)