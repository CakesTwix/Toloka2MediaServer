"""Functions for working with torrents"""
import logging

from toloka2transmission.config import titles, toloka
from toloka2transmission.transmission import TransmissionClient
from toloka2transmission.utils.general import get_numbers


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

        # Update date and write
        titles[title]["PublishDate"] = torrent_toloka.registered_date
        with open("titles.ini", "w", encoding="utf-8") as conf:
            titles.write(conf)

    # Get all torrents and get one by name
    for torrent in TransmissionClient.get_torrents():
        if titles[title]["torrent_name"] == torrent.name or force:
            # Remove old torrent
            TransmissionClient.remove_torrent(torrent.id)
                
            # Download torrent file
            new_torrent = TransmissionClient.get_torrent(
                TransmissionClient.add_torrent(
                    toloka.download_torrent(f"{toloka.toloka_url}/{torrent_toloka.torrent_url}"),
                    download_dir=titles[title]["download_dir"],
                ).id
            )

            # Rename episodes
            if titles[title]["episode_number"]:
                # New torrent Files
                for name in new_torrent.get_files():
                    # Episode S1E01.mkv
                    new_name = f"Episode S{titles[title]['season_number']}E{get_numbers(name.name)[int(titles[title]['episode_number'])]}{titles[title]['ext_name']}"
                    TransmissionClient.rename_torrent_path(
                        new_torrent.id, name.name, new_name
                    )

            # Rename Torrent
            TransmissionClient.rename_torrent_path(
                new_torrent.id,
                new_torrent.name,
                titles[title]["torrent_name"],
            )

            # Check old files
            TransmissionClient.verify_torrent(new_torrent.id)
            TransmissionClient.start_torrent(new_torrent.id)

            # No need check next torrents
            break
