"""Entering the program, this is where it all starts"""
import argparse
import configparser
import logging
import sys
import re

from toloka2MediaServer.config import app, titles, toloka, selectedClient

# Dynamic client import based on selected client
client_module = f"toloka2MediaServer.clients.{selectedClient.lower()}"
utils_module = f"toloka2MediaServer.utils.{selectedClient.lower()}"
client = __import__(client_module, fromlist=['client']).client
update = __import__(utils_module, fromlist=['update']).update
add = __import__(utils_module, fromlist=['add']).add

from toloka2MediaServer.utils.general import get_numbers

# Setup argparse
parser = argparse.ArgumentParser(description="Console utility for updating torrents from Toloka.")
parser.add_argument("-c", "--codename", type=str, help="Codename of the title")
parser.add_argument("-n", "--num", type=str, help="Get list of numbers from string")
parser.add_argument("-a", "--add", type=str, help="Add new release to config.")
parser.add_argument("-u", "--url", type=str, help="toloka url to release")
parser.add_argument("-s", "--season", type=str, help="season number")
parser.add_argument("-i", "--index", type=str, help="series index")
parser.add_argument("-t", "--title", type=str, help="series name")
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
    
    # Extract the name and year from the torrent name
    matchName = re.search(r'[\/|]([^\/|\(]+)', torrent.name)
    matchYear = re.search(r'\((\d{4})\)', torrent.name)
    if matchName:
        suggested_name = f"{matchName.group(1)} ({matchYear.group(1)})".strip()
        suggested_name = re.sub(r'\s+', ' ', suggested_name)
        suggested_codename = re.sub(r'\W+', '', matchName.group(1)).strip()
    else:
        suggested_name = "No match found"
        suggested_codename = "No match found"

    
    codename = input(f"Default:{suggested_codename}. Enter the codename: ") or suggested_codename
    config_update = configparser.RawConfigParser()
    config_update.add_section(codename)
    config_update.set(codename, "Guid", torrent.url)

    # Collect additional data
    season_number = input("Enter the season number: ")
    season_number = season_number.zfill(2)
    ext_name = input('Enter the file extension, e.g., ".mkv": ') or ".mkv"
    default_download_dir = app["Toloka"]["default_download_dir"]
    download_dir = input(f"Default: {default_download_dir}:. Enter the download directory path.  ") or default_download_dir
    torrent_name = input(f"Default: {suggested_name}. Enter the directory name for the downloaded files: ") or suggested_name
    release_group = input("Enter the release group name, or it will default to the torrent's author: ") or torrent.author
    default_meta = app["Toloka"]["default_meta"]
    meta = input(f"Default: {default_meta}. Enter additional metadata tags: ") or default_meta

    add(torrent, codename, config_update, season_number, ext_name, download_dir, torrent_name, release_group, meta)
    sys.exit()

# Update specific or all anime
if args.codename:
    update(args.codename, args.force)
else:
    for title in titles.sections():
        update(title, args.force)