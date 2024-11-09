# bittorrent_client.py
from abc import ABC, abstractmethod


class BittorrentClient(ABC):
    def __init__(self):
        self._tags = None
        self._category = None

    @abstractmethod
    def add_torrent(self, torrents, category, tags, is_paused, download_dir):
        """Add a new torrent."""
        pass

    @abstractmethod
    def get_torrent_info(
        self, status_filter, category, tags, sort, reverse, torrent_hash
    ):
        """Retrieve information about torrents."""
        pass

    @abstractmethod
    def get_files(self, torrent_hash):
        """Get files for a specific torrent."""
        pass

    @abstractmethod
    def rename_file(self, torrent_hash, old_path, new_path):
        """Rename a file within a torrent."""
        pass

    @abstractmethod
    def rename_folder(self, torrent_hash, old_path, new_path):
        """Rename a folder within a torrent."""
        pass

    @abstractmethod
    def rename_torrent(self, torrent_hash, new_torrent_name):
        """Rename a torrent."""
        pass

    @abstractmethod
    def resume_torrent(self, torrent_hashes):
        """Resume paused torrents."""
        pass

    @abstractmethod
    def delete_torrent(self, delete_files, torrent_hashes):
        """Delete torrents."""
        pass

    @abstractmethod
    def recheck_torrent(self, torrent_hashes):
        """Recheck torrents."""
        pass

    @abstractmethod
    def end_session(self, torrent_hashes):
        """End client session."""
        pass

    @property
    def tags(self):
        """Get the tags."""
        return self._tags

    @tags.setter
    def tags(self, value):
        """Set the tags."""
        self._tags = value

    @property
    def category(self):
        """Get the category."""
        return self._category

    @category.setter
    def category(self, value):
        """Set the category."""
        self._category = value
