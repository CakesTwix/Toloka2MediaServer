import qbittorrentapi

from toloka2MediaServer.clients.bittorrent_client import BittorrentClient


class QbittorrentClient(BittorrentClient):
    def __init__(self, config):
        """Initialize and log in to the qBittorrent client."""
        try:
            super().__init__()
            self.api_client = qbittorrentapi.Client(
                host=config.app_config[config.application_config.client]["host"],
                port=config.app_config[config.application_config.client]["port"],
                username=config.app_config[config.application_config.client][
                    "username"
                ],
                password=config.app_config[config.application_config.client][
                    "password"
                ],
            )

            self.category = config.app_config[config.application_config.client][
                "category"
            ]
            self.tags = config.app_config[config.application_config.client]["tag"]

            self.api_client.auth_log_in()
            config.logger.info("Connected to qBittorrent client successfully.")
        except qbittorrentapi.LoginFailed as e:
            config.logger.critical(
                "Failed to log in to qBittorrent: Incorrect login details."
            )
            raise
        except qbittorrentapi.APIConnectionError as e:
            config.logger.critical(
                "Failed to connect to qBittorrent: Check connection details."
            )
            raise
        except Exception as e:
            config.logger.critical(f"An unexpected error occurred: {str(e)}")
            raise

    def add_torrent(self, torrents, category, tags, is_paused, download_dir):
        return self.api_client.torrents.add(
            torrent_files=torrents, category=category, tags=tags, is_paused=is_paused, download_path=download_dir
        )

    def get_torrent_info(
        self, status_filter, category, tags, sort, reverse, torrent_hash=None
    ):
        return self.api_client.torrents_info(
            status_filter=status_filter,
            category=category,
            tag=tags,
            sort=sort,
            reverse=reverse,
        )

    def get_files(self, torrent_hash):
        return self.api_client.torrents_files(torrent_hash)

    def rename_file(self, torrent_hash, old_path, new_path):
        return self.api_client.torrents_rename_file(
            torrent_hash=torrent_hash, old_path=old_path, new_path=new_path
        )

    def rename_folder(self, torrent_hash, old_path, new_path):
        return self.api_client.torrents_rename_folder(
            torrent_hash=torrent_hash, old_path=old_path, new_path=new_path
        )

    def rename_torrent(self, torrent_hash, new_torrent_name):
        return self.api_client.torrents_rename(
            torrent_hash=torrent_hash, new_torrent_name=new_torrent_name
        )

    def resume_torrent(self, torrent_hashes):
        return self.api_client.torrents_resume(torrent_hashes=torrent_hashes)

    def delete_torrent(self, delete_files, torrent_hashes):
        return self.api_client.torrents_delete(
            delete_files=delete_files, torrent_hashes=torrent_hashes
        )

    def recheck_torrent(self, torrent_hashes):
        return self.api_client.torrents_recheck(torrent_hashes=torrent_hashes)

    def end_session(self):
        return self.api_client.auth_log_out()
