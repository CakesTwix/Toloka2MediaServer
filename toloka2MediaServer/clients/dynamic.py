def dynamic_client_init(config):
    """Dynamically import and initialize the torrent client based on the selected client in config."""
    client_module_name = (
        f"toloka2MediaServer.clients.{config.application_config.client.lower()}"
    )
    client_class_name = f"{config.application_config.client.capitalize()}Client"

    try:
        # Dynamically import the client module and get the client class
        client_module = __import__(client_module_name, fromlist=[client_class_name])
        client_class = getattr(client_module, client_class_name)
        # Initialize the client instance
        return client_class(config)
    except Exception as e:
        config.logger.critical(
            f"Failed to initialize the {config.application_config.client} client: {str(e)}"
        )
        raise
