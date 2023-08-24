"""Functions for working with torrents"""
import logging
import sys

import requests

from toloka2transmission.config import app, titles
from toloka2transmission.transmission import TransmissionClient
from toloka2transmission.utils.general import get_numbers


def search(query):
    """Returns JSON of torrents by search"""
    return requests.get(
        f'{app["Jackett"]["url"]}/api/v2.0/indexers/all/results?apikey={app["Jackett"]["api_key"]}&Query={query}&Tracker[]=toloka',
        timeout=10,
    ).json()


def update(title: str, force: bool):
    # All ok, do magic ^_^
    # Search Anime by "search query" and check Guid
    toloka = search(titles[title]["name"])["Results"]

    for torrent in toloka[:10]:
        if torrent["Guid"] == titles[title]["guid"]:
            toloka = torrent
            break

    # Not found by guid
    if isinstance(toloka, list):
        logging.critical("Not found! Check Guid!")
        sys.exit()

    # Check if have updates by date
    if titles[title]["PublishDate"] == toloka["PublishDate"]:
        logging.info(f"Same date! : {toloka['Title']}")
        return
    else:
        # We have some changes! Do redownload torrent
        logging.info(f"Date is different! : {toloka['Title']}")

        # Update date and write
        titles[title]["PublishDate"] = toloka["PublishDate"]
        with open("titles.ini", "w", encoding="utf-8") as conf:
            titles.write(conf)

    # Get all torrents and get one by name
    for torrent in TransmissionClient.get_torrents():
        if titles[title]["torrent_name"] == torrent.name or force:
            # Remove old torrent
            if not force:
                TransmissionClient.remove_torrent(torrent.id)

            # Download torrent file
            new_torrent = TransmissionClient.get_torrent(
                TransmissionClient.add_torrent(
                    toloka["Link"],
                    download_dir=titles[title]["download_dir"],
                ).id
            )

            # Rename episodes
            if titles[title]["episode_number"]:
                # New torrent Files
                for name in new_torrent.get_files():
                    # Episode S1E01.mkv
                    logging.debug(
                        f"Episode S{titles[title]['season_number']}E{get_numbers(name.name)[int(titles[title]['episode_number'])]}{titles[title]['ext_name']}"
                    )
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
