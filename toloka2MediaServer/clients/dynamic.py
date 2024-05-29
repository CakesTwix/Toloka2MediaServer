import logging
from toloka2MediaServer.config import app, selectedClient

# Set Logging
logger = logging.getLogger(__name__)

def dynamic_client_init():
    """Dynamically import and initialize the torrent client based on the selected client in config."""
    client_module_name = f"toloka2MediaServer.clients.{selectedClient.lower()}"
    client_class_name = f"{selectedClient.capitalize()}Client"

    try:
        # Dynamically import the client module and get the client class
        client_module = __import__(client_module_name, fromlist=[client_class_name])
        client_class = getattr(client_module, client_class_name)
        # Initialize the client instance
        return client_class()
    except Exception as e:
        logger = logging.getLogger(__name__).critical(f"Failed to initialize the {selectedClient} client: {str(e)}")
        raise