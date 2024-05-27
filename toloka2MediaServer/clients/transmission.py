import logging
import sys

from transmission_rpc import Client
from transmission_rpc.error import TransmissionConnectError

from toloka2MediaServer.config import app, selectedClient

# Set Logging
logging.basicConfig(level=app["Python"]["logging"])

def initialize_client():
    """Initialize and log in to the Transmission client."""
    try:
        client = Client(
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
    return client

client = initialize_client()