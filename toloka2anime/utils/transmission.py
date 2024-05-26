"""Functions for working with torrents"""
import logging

from toloka2anime.config import titles, toloka
from toloka2anime.clients.transmission import client
from toloka2anime.utils.general import get_numbers


def update(title: str, force: bool):
    # All ok, do magic ^_^
    # Search Anime by "search query" and check Guid
    torrent_toloka = toloka.get_torrent(f"{toloka.toloka_url}/{titles[title]['guid']}")

    # Check if have updates by date
    if titles[title]["PublishDate"] in torrent_toloka.registered_date:
        logging.info(f"Same date! : {torrent_toloka.name}")
        return
    else:
        # We have some changes! Do redownload torrent
        logging.info(f"Date is different! : {torrent_toloka.name}")

    # Get all torrents and get one by name
    for torrent in client.get_torrents():
        if titles[title]["torrent_name"] == torrent.name or force:
            # Remove old torrent
            if force != True:
                client.remove_torrent(torrent.id)
                
            # Download torrent file
            new_torrent = client.get_torrent(
                client.add_torrent(
                    toloka.download_torrent(f"{toloka.toloka_url}/{torrent_toloka.torrent_url}"),
                    download_dir=titles[title]["download_dir"],
                ).id
            )

            # Rename episodes
            if titles[title]["episode_number"]:
                # New torrent Files
                for name in new_torrent.get_files():
                    # Episode S1E01.mkv
                    new_name = f"{titles[title]['torrent_name']} S{titles[title]['season_number']}E{get_numbers(name.name)[int(titles[title]['episode_number'])]}{titles[title]['ext_name']}".replace(" ", ".")
                    client.rename_torrent_path(
                        new_torrent.id, name.name, new_name
                    )

            # Rename Torrent
            client.rename_torrent_path(
                new_torrent.id,
                new_torrent.name,
                titles[title]["torrent_name"],
            )

            # Check old files
            client.verify_torrent(new_torrent.id)
            client.start_torrent(new_torrent.id)

            # Update date and write
            titles[title]["PublishDate"] = torrent_toloka.registered_date
            with open("titles.ini", "w", encoding="utf-8") as conf:
                titles.write(conf)

            # No need check next torrents
            break

# Add new anime to titles.ini
def add(torrent, codename, config_update, season_number, ext_name, download_dir, torrent_name):
    new_torrent = client.get_torrent(
        client.add_torrent(
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
        new_name = f"{torrent_name} S{season_number}E{get_numbers(name.name)[episode_number]}{ext_name}".replace(" ", ".")
        client.rename_torrent_path(new_torrent.id, name.name, new_name)

    # Rename Torrent
    client.rename_torrent_path(
        new_torrent.id, new_torrent.name, torrent_name
    )

    # Start
    client.start_torrent(new_torrent.id)

    # Write to config
    with open("titles.ini", "a", encoding="utf-8") as f:
        config_update.write(f)
