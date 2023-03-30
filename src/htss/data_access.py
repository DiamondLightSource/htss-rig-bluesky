from databroker.client import CatalogOfBlueskyRuns
from tiled.client import from_uri

from .names import server_name


def get_client() -> CatalogOfBlueskyRuns:
    return from_uri(f"http://{server_name()}:8000")
