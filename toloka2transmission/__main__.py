"""Entering the program, this is where it all starts"""
import argparse
import logging
import sys
import requests
from transmission_rpc import Client
from transmission_rpc.error import TransmissionConnectError
from transmission_rpc.utils import format_size

from toloka2transmission.config import app, titles
from toloka2transmission.utils.general import getNumbers

# Instantiate the parser
parser = argparse.ArgumentParser(
    description="Консольна утиліта для оновлень торрентів із Toloka. "
)

# Required positional argument
parser.add_argument("-c", "--codename", type=str, help="Коднейм тайтла")
parser.add_argument('-n', '--num', type=str, help='Get list of numbers from string')


args = parser.parse_args()

# Need send only list of numbers
if args.num:
    print(getNumbers(args.num))
    sys.exit()

# Set Logging
logging.basicConfig(level=logging.INFO)

# Init
try:
    TransmissionClient = Client(
        host=app["Transmission"]["host"],
        port=app["Transmission"]["port"],
        username=app["Transmission"]["username"],
        password=app["Transmission"]["password"],
        path=app["Transmission"]["rpc"],
        protocol=app["Transmission"]["protocol"],
    )
    # For init information
    downloaded = format_size(
        TransmissionClient.session_stats().current_stats.downloaded_bytes
    )
    uploaded = format_size(
        TransmissionClient.session_stats().current_stats.uploaded_bytes
    )

    logging.info(f"Downloaded: {downloaded[0]} {downloaded[1]}")
    logging.info(f"Uploaded: {uploaded[0]} {uploaded[1]}")
except TransmissionConnectError:
    logging.critical("Not connection!")
    sys.exit()

# All ok, do magic ^_^
for torrent in TransmissionClient.get_torrents():
    if titles[args.codename]["torrent_name"] == torrent.name:
        logging.debug(torrent.name)

        toloka = requests.get(
            f'{app["Jackett"]["url"]}/api/v2.0/indexers/all/results?apikey={app["Jackett"]["api_key"]}&Query={titles[args.codename]["name"]}&Tracker[]=toloka'
        ).json()
        logging.info(toloka["Results"][0]["Guid"])
        if input("Воно? 0 - ні, інаше - так:\n") == "0":
            sys.exit()

        # Check if have updates by date
        if titles[args.codename]["PublishDate"] == toloka["Results"][0]["PublishDate"]:
            logging.info("Same date!")
            sys.exit()
        else:
            logging.info("Date is different!")

            # Update date and write
            titles[args.codename]["PublishDate"] = toloka["Results"][0]["PublishDate"]
            with open("titles.ini", "w", encoding="utf-8") as conf:
                titles.write(conf)

            # Remove old torrent
            TransmissionClient.remove_torrent(torrent.id)

            # Download torrent file
            new_torrent = TransmissionClient.get_torrent(
                TransmissionClient.add_torrent(
                    toloka["Results"][0]["Link"],
                    download_dir=titles[args.codename]["download_dir"],
                ).id
            )

            # Rename episodes
            if titles[args.codename]["episode_number"]:
                # New torrent Files
                for name_id, name in enumerate(new_torrent.get_files()):
                    logging.info(name.name)
                    # Episode S1E01.mkv
                    new_name = f"Episode S{titles[args.codename]['season_number']}E{getNumbers(name.name)[int(titles[args.codename]['episode_number'])]}{titles[args.codename]['ext_name']}"
                    TransmissionClient.rename_torrent_path(
                        new_torrent.id, name.name, new_name
                    )

            # Rename Torrent
            TransmissionClient.rename_torrent_path(
                new_torrent.id, new_torrent.name, titles[args.codename]["torrent_name"]
            )

            # Check old files
            TransmissionClient.verify_torrent(new_torrent.id)
            TransmissionClient.start_torrent(new_torrent.id)

        # toloka.json()["Results"][0]["Link"] # Torrent url
