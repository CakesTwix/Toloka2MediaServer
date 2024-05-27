import logging
import qbittorrentapi

from toloka2MediaServer.config import app, selectedClient

# Set Logging
logging.basicConfig(level=app["Python"]["logging"])

def initialize_client():
    """Initialize and log in to the qBittorrent client."""
    try:
        client = qbittorrentapi.Client(
            host=app[selectedClient]["host"],
            port=app[selectedClient]["port"],
            username=app[selectedClient]["username"],
            password=app[selectedClient]["password"],
        )
        client.auth_log_in()
        logging.info("Connected to qBit")
    except qbittorrentapi.LoginFailed:
        logging.critical("qBit wrong login details")
        raise
    except qbittorrentapi.APIConnectionError:
        logging.critical("qBit wrong connection details")
        raise
    return client

client = initialize_client()