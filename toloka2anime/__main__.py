"""Entering the program, this is where it all starts"""
import argparse
import configparser
import logging
import sys
from toloka2anime.config import app, titles, toloka, selectedClient

match selectedClient:
    case "Transmission":
        from toloka2anime.clients.transmission import client
        from toloka2anime.utils.transmission import update, add
    case "qBittorrent":
        from toloka2anime.clients.qbit import client
        from toloka2anime.utils.qbit import update, add

from toloka2anime.utils.general import get_numbers

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

    ext_name = input('Введіть розширення у файлу, наприклад ".mkv": ') or ".mkv"
    download_dir = input("Введіть путь, куди завантажити файли: ")
    torrent_name = input("Введіть назву директорії, куди будуть завантажені файли: ")
    release_group = input("Введіть назву реліз групи. У разі відсутності вибору буде автор роздачи: ") or torrent.author
    meta = input("Введіть додаткові теги метаданих. у разі відсутності вибору буде [WEBRip-1080p][UK+JA]: ") or "[WEBRip-1080p][UK+JA]"

    add(torrent, codename, config_update, season_number, ext_name, download_dir, torrent_name, release_group, meta)
    sys.exit()

# Update this anime
if args.codename:
    update(args.codename, args.force)
    sys.exit()

# Update all titles
for title in titles.sections():
    update(title, args.force)
