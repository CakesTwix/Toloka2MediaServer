from transmission_rpc import Client
from transmission_rpc.error import TransmissionConnectError

from toloka2MediaServer.clients.bittorrent_client import BittorrentClient

class TransmissionClient(BittorrentClient):
    def __init__(self, config):
        """Initialize and log in to the Transmission client."""
        try:
            super().__init__()
            self.api_client = Client(
                host=config.app_config[config.application_config.client]["host"],
                port=config.app_config[config.application_config.client]["port"],
                username=config.app_config[config.application_config.client]["username"],
                password=config.app_config[config.application_config.client]["password"],
                path=config.app_config[config.application_config.client]["rpc"],
                protocol=config.app_config[config.application_config.client]["protocol"],
            )
                        
            self.category = config.app_config[config.application_config.client]["category"]
            self.tags = config.app_config[config.application_config.client]["tag"]
            
            config.logger.info(f"Connected to: {config.application_config.client}")
        except TransmissionConnectError:
            config.logger.critical(f"{config.application_config.client} wrong connection details")
            raise

    def add_torrent(self, torrents, category, tags, is_paused, download_dir):
        labels=[category,tags]
        return self.api_client.add_torrent(torrent=torrents, paused=is_paused, labels=labels, download_dir=download_dir).id

    def get_torrent_info(self, status_filter, category, tags, sort, reverse, torrent_hash):
        return self.api_client.get_torrent(torrent_hash)

    def get_files(self, torrent_hash):
        return self.api_client.get_files(torrent_hash)

    def rename_file(self, torrent_hash, old_path, new_path):
        return self.api_client.rename_torrent_path(torrent_hash, old_path, new_path)

    def rename_folder(self, torrent_hash, old_path, new_path):
        return self.api_client.rename_torrent_path(torrent_hash, old_path, new_path)

    def rename_torrent(self, torrent_hash, new_torrent_name):
        return True

    def resume_torrent(self, torrent_hashes):
        return self.api_client.start_torrent(torrent_hashes)

    def delete_torrent(self, delete_files, torrent_hashes):
        return self.api_client.remove_torrent(torrent_hashes, delete_data=delete_files)

    def recheck_torrent(self, torrent_hashes):
        return self.api_client.verify_torrent(torrent_hashes)
    
    def end_session(self):
        self.api_client = None