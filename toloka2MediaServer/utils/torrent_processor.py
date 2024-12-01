"""Functions for working with torrents"""

import time

from toloka2MediaServer.clients.bittorrent_client import BittorrentClient

from toloka2MediaServer.config_parser import update_config
from toloka2MediaServer.models.operation_result import OperationResult
from toloka2MediaServer.models.title import Title, title_to_config
from toloka2MediaServer.utils.general import (
    get_numbers,
    replace_second_part_in_path,
    get_folder_name_from_path,
)


def process_torrent(config, title, torrent, new=False):
    """Common logic to process torrents, either updating or adding new ones"""
    title.publish_date = torrent.date

    tolokaTorrentFile = config.toloka.download_torrent(
        f"{config.toloka.toloka_url}/{torrent.torrent_url}"
    )

    category = config.client.category
    tag = config.client.tags

    add_torrent_response = config.client.add_torrent(
        torrents=tolokaTorrentFile,
        category=category,
        tags=[tag],
        is_paused=True,
        download_dir=title.download_dir,
    )
    time.sleep(config.application_config.client_wait_time)
    if config.application_config.client == "qbittorrent":
        filtered_torrents = config.client.get_torrent_info(
            status_filter="paused",
            category=category,
            tags=tag,
            sort="added_on",
            reverse=True,
        )
        added_torrent = filtered_torrents[0]
        title.hash = added_torrent.info.hash
        get_filelist = config.client.get_files(title.hash)

    else:
        added_torrent = config.client.get_torrent_info(
            status_filter=["paused"],
            category=category,
            tags=[tag],
            sort="added_on",
            reverse=True,
            torrent_hash=add_torrent_response,
        )
        title.hash = added_torrent.hash_string
        get_filelist = added_torrent.get_files()

    config.logger.debug(added_torrent)

    first_fileName = get_filelist[0].name

    if new:

        title.guid = torrent.url
        # Extract numbers from the filename
        numbers = get_numbers(first_fileName)

        if title.episode_index == -1:
            # Display the numbers to the user, starting count from 1
            print(
                f"{first_fileName}\nEnter the order number of the episode index from the list below:"
            )
            for index, number in enumerate(numbers, start=1):
                print(f"{index}: {number}")

            # Get user input and adjust for 0-based index
            episode_order = int(input("Your choice (use order number): "))
            episode_index = episode_order - 1  # Convert to 0-based index
            source_episode_number = numbers[episode_index]
            print(f"You selected episode number: {numbers[episode_index]}")

            adjustment_input = input(
                "Enter the adjustment value (e.g., '+9' or '-3', default is 0): "
            ).strip()
            adjusted_episode_number = int(adjustment_input) if adjustment_input else 0

            if adjusted_episode_number != 0:
                # Calculate new episode number considering adjustment and preserve leading zeros if any
                adjusted_episode = str(
                    int(source_episode_number) + adjusted_episode_number
                ).zfill(len(source_episode_number))
            else:
                adjusted_episode = source_episode_number
            print(f"Adjusted episode number: {adjusted_episode}")

            title.episode_index = episode_index
            title.adjusted_episode_number = adjusted_episode_number

    for file in get_filelist:
        ext_name = file.name.split('.')[-1]

        source_episode = get_numbers(file.name)[title.episode_index]
        calculated_episode = str(
            int(source_episode) + title.adjusted_episode_number
        ).zfill(len(source_episode))

        if config.application_config.enable_dot_spacing_in_file_name:
            # Use dots as separators and no hyphen
            new_name = f"{title.torrent_name}.S{title.season_number}E{calculated_episode}.{title.meta}{title.release_group}.{ext_name}"
            # Just in case replace spaces if any in name, meta or release group
            new_name = new_name.replace("  ", ".").replace(" ", ".")
        else:
            # Use spaces as separators and a hyphen before release_group
            new_name = f"{title.torrent_name} S{title.season_number}E{calculated_episode} {title.meta}-{title.release_group}.{ext_name}"

        if config.application_config.client == "qbittorrent":
            new_path = replace_second_part_in_path(file.name, new_name)
        else:
            new_path = new_name
        config.client.rename_file(
            torrent_hash=title.hash, old_path=file.name, new_path=new_path
        )

    folderName = f"{title.torrent_name} S{title.season_number} {title.meta}[{title.release_group}]"
    if config.application_config.enable_dot_spacing_in_file_name:
        folderName = folderName.replace("  ", ".").replace(" ", ".")

    old_path = get_folder_name_from_path(first_fileName)
    config.client.rename_folder(
        torrent_hash=title.hash, old_path=old_path, new_path=folderName
    )
    config.client.rename_torrent(torrent_hash=title.hash, new_torrent_name=folderName)

    if new:
        config.client.resume_torrent(torrent_hashes=title.hash)
    else:
        config.client.recheck_torrent(torrent_hashes=title.hash)
        config.client.resume_torrent(torrent_hashes=title.hash)

    titleConfig = title_to_config(title)
    update_config(titleConfig, title.code_name)

    return config.operation_result


def update(config, title):
    config.operation_result.titles_references.append(title)
    if title == None:
        config.operation_result.operation_logs.append("Title not found")
        return config.operation_result
    guid = title.guid.strip('"') if title.guid else ""
    torrent = config.toloka.get_torrent(f"{config.toloka.toloka_url}/{guid}")
    config.operation_result.torrent_references.append(torrent)
    if title.publish_date not in torrent.date:
        message = f"Date is different! : {torrent.name}"
        config.operation_result.operation_logs.append(message)
        config.logger.info(message)
        if not config.args.force:
            config.client.delete_torrent(delete_files=False, torrent_hashes=title.hash)
        config.operation_result = process_torrent(config, title, torrent)
    else:
        message = f"Update not required! : {torrent.name}"
        config.operation_result.operation_logs.append(message)
        config.logger.info(message)

    return config.operation_result


# torrent, title, operation_result, logger, toloka, client, application_config, titles_config, operation_result


def add(config, title, torrent):
    config.operation_result.titles_references.append(title)
    config.operation_result.torrent_references.append(torrent)
    config.operation_result = process_torrent(config, title, torrent, new=True)
    config.client.end_session()

    return config.operation_result
