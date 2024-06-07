from dataclasses import dataclass
import configparser

@dataclass
class Title:
    code_name: str = ""
    episode_index: int = -1
    season_number: str = ""
    ext_name: str = ""
    torrent_name: str = ""
    download_dir: str = ""
    publish_date: str = ""
    release_group: str = ""
    meta: str = ""
    hash: str = ""
    adjusted_episode_number: int = 0
    guid: str = ""
    
def title_to_config(title):
    """
    Transform Title class back to specified section of configparser.ConfigParser() 

    Args:
        title (Title): created by config_to_title

    Returns:
        config (configparser.ConfigParser()): parser with updated section
    """
    config = configparser.ConfigParser()
    config[title.code_name] = {
        'episode_index': str(title.episode_index),
        'season_number': title.season_number,
        'ext_name': title.ext_name,
        'torrent_name': f'"{title.torrent_name}"',
        'download_dir': title.download_dir,
        'publish_date': title.publish_date,
        'release_group': title.release_group,
        'meta': title.meta,
        'hash': title.hash,
        'adjusted_episode_number': str(title.adjusted_episode_number),
        'guid': title.guid
    }
    
    return config

def config_to_title(config, code_name):
    """
    Transform specified section of configparser.ConfigParser() into Title class

    Args:
        config (configparser.ConfigParser()): titles.ini
        code_name (str): name of the section from config

    Returns:
        Title: title class instance of config section
    """
    if code_name not in config:
        return None

    section = config[code_name]
    return Title(
        code_name=code_name,
        episode_index=int(section.get('episode_index', -1)),
        season_number=section.get('season_number', ''),
        ext_name=section.get('ext_name', ''),
        torrent_name=section.get('torrent_name', '').strip('"'),
        download_dir=section.get('download_dir', ''),
        publish_date=section.get('publish_date', ''),
        release_group=section.get('release_group', ''),
        meta=section.get('meta', ''),
        hash=section.get('hash', ''),
        adjusted_episode_number=int(section.get('adjusted_episode_number', 0)),
        guid=section.get('guid', '')
    )