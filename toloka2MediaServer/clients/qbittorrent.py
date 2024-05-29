import logging
import qbittorrentapi

from toloka2MediaServer.clients.bittorrent_client import BittorrentClient
from toloka2MediaServer.config import app, selectedClient

# Set Logging
logging.basicConfig(level=app["Python"]["logging"])
class QBittorrentClient(BittorrentClient):
    def __init__(self):
        """Initialize and log in to the qBittorrent client."""
        try:
            self.api_client = qbittorrentapi.Client(
                host=app[selectedClient]["host"],
                port=app[selectedClient]["port"],
                username=app[selectedClient]["username"],
                password=app[selectedClient]["password"],
            )
            self.api_client.auth_log_in()
            logging.info("Connected to qBittorrent client successfully.")
        except qbittorrentapi.LoginFailed as e:
            logging.critical("Failed to log in to qBittorrent: Incorrect login details.")
            raise
        except qbittorrentapi.APIConnectionError as e:
            logging.critical("Failed to connect to qBittorrent: Check connection details.")
            raise
        except Exception as e:
            logging.critical(f"An unexpected error occurred: {str(e)}")
            raise
    
    def add_torrent(self, torrent_file, category, tags, is_paused):
        return self.api_client.torrents.add(torrent_files=torrent_file, category=category, tags=tags, is_paused=is_paused)

    def get_torrent_info(self, status_filter, category, tags, sort, reverse):
        return self.api_client.torrents_info(status_filter=status_filter, category=category, tags=tags, sort=sort, reverse=reverse)

    def get_files(self, torrent_hash):
        return self.api_client.torrents_files(torrent_hash)

    def rename_file(self, torrent_hash, old_path, new_path):
        return self.api_client.torrents_rename_file(torrent_hash=torrent_hash, old_path=old_path, new_path=new_path)

    def rename_folder(self, torrent_hash, old_path, new_path):
        return self.api_client.torrents_rename_folder(torrent_hash=torrent_hash, old_path=old_path, new_path=new_path)

    def rename_torrent(self, torrent_hash, new_torrent_name):
        return self.api_client.torrents_rename(torrent_hash=torrent_hash, new_torrent_name=new_torrent_name)

    def resume_torrent(self, torrent_hashes):
        return self.api_client.torrents_resume(torrent_hashes=torrent_hashes)

    def delete_torrent(self, delete_files, torrent_hashes):
        return self.api_client.torrents_delete(delete_files=delete_files, torrent_hashes=torrent_hashes)

    def recheck_torrent(self, torrent_hashes):
        return self.api_client.torrents_recheck(torrent_hashes=torrent_hashes)