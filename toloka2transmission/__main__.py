"""Entering the program, this is where it all starts"""
import argparse
import configparser
import logging
import sys

from toloka2transmission.config import app, titles, toloka
from toloka2transmission.transmission import TransmissionClient
from toloka2transmission.utils.general import get_numbers
from toloka2transmission.utils.transmission import update

# Instantiate the parser
parser = argparse.ArgumentParser(
    description="Консольна утиліта для оновлень торрентів із Toloka."
)

# Required positional argument
parser.add_argument("-c", "--codename", type=str, help="Коднейм тайтла")
parser.add_argument("-n", "--num", type=str, help="Отримати список чисел з рядка")
parser.add_argument("-a", "--add", type=str, help="Додати нове аніме в конфіг.")
parser.add_argument(
    "-f",
    "--force",
    action=argparse.BooleanOptionalAction,
    help="Примусово качати торрент, не дивлячись на його відсутність.",
)

args = parser.parse_args()

# Need send only list of numbers
if args.num:
    print(get_numbers(args.num))
    sys.exit()

# Set Logging
logging.basicConfig(level=app["Python"]["logging"])

# Add new anime to titles.ini
if args.add:
    torrent = toloka.search(args.add)
    
    # Check results
    if len(torrent) == 0:
        logging.info("Нічого не знайшли :(")
        sys.exit()

    for index, item in enumerate(torrent[:10]):
        print(f"{index} : {item.name} - {item.url}")

    torrent = torrent[int(input("Введіть номер потрібного торрента: "))]

    codename = input("Enter the codename: ")
    config_update = configparser.RawConfigParser()
    config_update.add_section(codename)
    config_update.set(codename, "Guid", torrent.url)

    # Get data
    season_number = input("Введіть номер сезону: ")

    ext_name = input('Введіть розширення у файлу, наприклад ".mkv": ')
    download_dir = input("Введіть путь, куди завантажити файли: ")
    torrent_name = input("Введіть назву директорії, куди будуть завантажені файли: ")

    # Download torrent file
    new_torrent = TransmissionClient.get_torrent(
        TransmissionClient.add_torrent(
            toloka.download_torrent(f"{toloka.toloka_url}/{torrent.download_link}"),
            download_dir=download_dir,
        ).id
    )

    episode_number = int(
        input(
            f"Введіть індекс серії\n{new_torrent.get_files()[0].name} : {get_numbers(new_torrent.get_files()[0].name)}: "
        )
    )

    # Write data
    config_update.set(codename, "episode_number", episode_number)
    config_update.set(codename, "season_number", season_number)
    config_update.set(codename, "ext_name", ext_name)
    config_update.set(codename, "torrent_name", torrent_name)
    config_update.set(codename, "download_dir", download_dir)
    config_update.set(codename, "publishdate", torrent.date)

    for name in new_torrent.get_files():
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

# Update this anime
if args.codename:
    update(args.codename, args.force)
    sys.exit()

# Update all titles
for title in titles.sections():
    update(title, args.force)
