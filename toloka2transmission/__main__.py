"""Entering the program, this is where it all starts"""
import argparse
import configparser
import logging
import sys

from transmission_rpc import Client
from transmission_rpc.error import TransmissionConnectError
from transmission_rpc.utils import format_size

from toloka2transmission.config import app, titles
from toloka2transmission.utils.general import get_numbers
from toloka2transmission.utils.transmission import search

# Instantiate the parser
parser = argparse.ArgumentParser(
    description="Консольна утиліта для оновлень торрентів із Toloka."
)

# Required positional argument
parser.add_argument("-c", "--codename", type=str, help="Коднейм тайтла")
parser.add_argument("-n", "--num", type=str, help="Отримати список чисел з рядка")
parser.add_argument("-a", "--add", type=str, help="Додати нове аніме в конфіг.")


args = parser.parse_args()

# Need send only list of numbers
if args.num:
    print(get_numbers(args.num))
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

# Add new anime to titles.ini
if args.add:
    torrent = search(args.add)["Results"][0]
    if (
        input(f"Воно? 0 - ні, інаше - так:\n {torrent['Title']} - {torrent['Guid']}")
        == "0"
    ):
        sys.exit()

    codename = input("Enter the codename: ")
    config_update = configparser.RawConfigParser()
    config_update.add_section(codename)
    config_update.set(codename, "name", args.add)

    # Get data
    season_number = input("Введіть номер сезону: ")

    ext_name = input('Введіть розширення у файлу, наприклад ".mkv": ')
    download_dir = input("Введіть путь, куди завантажити файли: ")
    torrent_name = input("Введіть назву директорії, куди будуть завантажені файли: ")

    # Download torrent file
    new_torrent = TransmissionClient.get_torrent(
        TransmissionClient.add_torrent(
            torrent["Link"],
            download_dir=download_dir,
        ).id
    )

    episode_number = int(
        input(f"Введіть індекс серії\n{get_numbers(new_torrent.get_files()[0].name)}: ")
    )

    # Write data
    config_update.set(codename, "episode_number", episode_number)
    config_update.set(codename, "season_number", season_number)
    config_update.set(codename, "ext_name", ext_name)
    config_update.set(codename, "torrent_name", torrent_name)
    config_update.set(codename, "download_dir", download_dir)
    config_update.set(codename, "publishdate", torrent["PublishDate"])

    for name_id, name in enumerate(new_torrent.get_files()):
        logging.info(name.name)
        # Episode S1E01.mkv
        new_name = f"Episode S{season_number}E{get_numbers(name.name)[episode_number]}{ext_name}"
        TransmissionClient.rename_torrent_path(new_torrent.id, name.name, new_name)

    # Rename Torrent
    TransmissionClient.rename_torrent_path(
        new_torrent.id, new_torrent.name, torrent_name
    )

    # Start
    TransmissionClient.start_torrent(new_torrent.id)

    # Write to config
    with open("titles.ini", "a", encoding="utf-8") as f:
        config_update.write(f)
    sys.exit()

# All ok, do magic ^_^
for torrent in TransmissionClient.get_torrents():
    if titles[args.codename]["torrent_name"] == torrent.name:
        logging.debug(torrent.name)

        toloka = search(titles[args.codename]["name"])
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
                    new_name = f"Episode S{titles[args.codename]['season_number']}E{get_numbers(name.name)[int(titles[args.codename]['episode_number'])]}{titles[args.codename]['ext_name']}"
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
