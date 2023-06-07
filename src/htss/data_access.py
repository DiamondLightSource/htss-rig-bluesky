from typing import Any, Mapping
from databroker.client import CatalogOfBlueskyRuns
from tiled.client import from_uri

from .names import server_name


def get_client() -> CatalogOfBlueskyRuns:
    return from_uri(f"http://{server_name()}:8000")


from pprint import pprint


def print_docs(name: str, doc: Mapping[str, Any]) -> None:
    pprint({"name": name, "doc": doc})
