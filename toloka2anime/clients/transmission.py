import logging
import sys

from transmission_rpc import Client
from transmission_rpc.error import TransmissionConnectError
from transmission_rpc.utils import format_size

from toloka2anime.config import app

# Set Logging
logging.basicConfig(level=app["Python"]["logging"])

# Init
try:
    TransmissionClient = Client(
        host=app["Transmission"]["host"],
        port=app["Transmission"]["port"],
        username=app["Transmission"]["username"],
        password=app["Transmission"]["password"],
        path=app["Transmission"]["rpc"],
        protocol=app["Transmission"]["protocol"],
    )
    # For init information
    downloaded = format_size(
        TransmissionClient.session_stats().current_stats.downloaded_bytes
    )
    uploaded = format_size(
        TransmissionClient.session_stats().current_stats.uploaded_bytes
    )

    logging.info(f"Downloaded: {downloaded[0]} {downloaded[1]}")
    logging.info(f"Uploaded: {uploaded[0]} {uploaded[1]}")
except TransmissionConnectError:
    logging.critical("Not connection!")
    sys.exit()
