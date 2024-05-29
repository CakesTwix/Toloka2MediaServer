import logging

from transmission_rpc import Client
from transmission_rpc.error import TransmissionConnectError

from toloka2MediaServer.clients.bittorrent_client import BittorrentClient
from toloka2MediaServer.config import app, selectedClient

# Set Logging
logging.basicConfig(level=app["Python"]["logging"])
class TransmissionClient(BittorrentClient):
    def __init__(self):
        """Initialize and log in to the Transmission client."""
        try:
            self.api_client = Client(
                host=app[selectedClient]["host"],
                port=app[selectedClient]["port"],
                username=app[selectedClient]["username"],
                password=app[selectedClient]["password"],
                path=app[selectedClient]["rpc"],
                protocol=app[selectedClient]["protocol"],
            )
            logging.info(f"Connected to: {selectedClient}")
        except TransmissionConnectError:
            logging.critical(f"{selectedClient} wrong connection details")
            raise

    def add_torrent(self, torrent_file, category, tags, is_paused):
        return self.api_client.add_torrent(filename=torrent_file, paused=is_paused)

    def get_torrent_info(self, status_filter, category, tags, sort, reverse):
        torrents = self.api_client.get_torrents()
        return [t for t in torrents if t.status == status_filter and t.category == category]

    def get_files(self, torrent_hash):
        return self.api_client.get_files(torrent_hash)

    def rename_file(self, torrent_hash, old_path, new_path):
        return self.api_client.rename_file(torrent_hash, old_path, new_path)

    def rename_folder(self, torrent_hash, old_path, new_path):
        return self.api_client.rename_folder(torrent_hash, old_path, new_path)

    def rename_torrent(self, torrent_hash, new_torrent_name):
        return self.api_client.rename_torrent(torrent_hash, new_torrent_name)

    def resume_torrent(self, torrent_hashes):
        return self.api_client.start_torrent(torrent_hashes)

    def delete_torrent(self, delete_files, torrent_hashes):
        return self.api_client.remove_torrent(torrent_hashes, delete_files=delete_files)

    def recheck_torrent(self, torrent_hashes):
        return self.api_client.verify_torrent(torrent_hashes)