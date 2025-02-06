import pytest
from blueapi.client.client import BlueapiClient
from blueapi.config import ApplicationConfig, RestConfig, StompConfig
from bluesky_stomp.models import BasicAuthentication

from htss_rig_bluesky.names import BEAMLINE


@pytest.fixture
def config() -> ApplicationConfig:
    if BEAMLINE == "p46":
        return ApplicationConfig(
            stomp=StompConfig(
                host="172.23.168.198",
                auth=BasicAuthentication(username="guest", password="guest"),  # type: ignore
            ),
            api=RestConfig(
                host="p46-blueapi.diamond.ac.uk", port=443, protocol="https"
            ),
        )
    else:
        return ApplicationConfig(
            stomp=StompConfig(
                host="localhost",
                auth=BasicAuthentication(username="guest", password="guest"),  # type: ignore
            )
        )


# This client will use authentication if a valid cached token is found
@pytest.fixture
def client(config: ApplicationConfig) -> BlueapiClient:
    return BlueapiClient.from_config(config=config)
