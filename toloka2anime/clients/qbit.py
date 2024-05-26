import logging
import sys
import qbittorrentapi

from toloka2anime.config import app
from toloka2anime.config import selectedClient

# Set Logging
logging.basicConfig(level=app["Python"]["logging"])
    
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
except qbittorrentapi.APIConnectionError:
    logging.critical("qBit wrong connection details")