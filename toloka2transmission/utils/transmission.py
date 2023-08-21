"""Functions for working with torrents"""
import requests
from toloka2transmission.config import app


def search(query):
    """Returns JSON of torrents by search"""
    return requests.get(
        f'{app["Jackett"]["url"]}/api/v2.0/indexers/all/results?apikey={app["Jackett"]["api_key"]}&Query={query}&Tracker[]=toloka',
        timeout=10,
    ).json()
