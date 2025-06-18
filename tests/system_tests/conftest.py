import base64
import os
from collections.abc import Generator
from pathlib import Path
from unittest import mock

import pytest
import requests
from blueapi.client.client import BlueapiClient
from blueapi.config import ApplicationConfig, OIDCConfig, RestConfig, StompConfig
from blueapi.service.model import Cache
from blueapi.worker.task import Task
from bluesky_stomp.models import BasicAuthentication
from pydantic import HttpUrl

from htss_rig_bluesky.names import BEAMLINE

CLIENT_ID = os.environ.get("CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "")
OIDC_TOKEN_ENDPOINT = os.environ.get("OIDC_TOKEN_ENDPOINT", "")


@pytest.fixture
def task_definition() -> dict[str, Task]:
    return {
        "step_scan_plan": Task(
            name="step_scan_plan",
            params={"detectors": "det", "motor": "sample_stage.theta"},
        ),
        "fly_and_collect_plan": Task(
            name="fly_and_collect_plan",
            params={"panda": "panda", "diff": "det"},
        ),
        "log_scan_plan": Task(
            name="log_scan_plan",
            params={"detectors": "det", "motor": "sample_stage.x"},
        ),
    }


@pytest.fixture
def config(tmp_path: Path) -> ApplicationConfig:
    if BEAMLINE == "p46":
        return ApplicationConfig(
            stomp=StompConfig(
                enabled=True,
                url=HttpUrl("http://p46-rabbitmq-daq.diamond.ac.uk:61613"),
                auth=BasicAuthentication(username="guest", password="guest"),  # type: ignore
            ),
            api=RestConfig(url=HttpUrl("https://p46-blueapi.diamond.ac.uk")),
            auth_token_path=tmp_path / "blueapi_cache",
        )
    return ApplicationConfig()


def get_access_token() -> str:
    response = requests.post(
        OIDC_TOKEN_ENDPOINT,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
        },
    )

    response.raise_for_status()
    return response.json().get("access_token", "")


# This client will use authentication if a valid cached token is found
@pytest.fixture
def client(
    config: ApplicationConfig,
) -> Generator[BlueapiClient, None, None] | BlueapiClient:
    if CLIENT_ID != "" and CLIENT_SECRET != "" and OIDC_TOKEN_ENDPOINT != "":
        # Initialize an empty cache to simulate a valid session
        cache = Cache(
            oidc_config=OIDCConfig(well_known_url="", client_id=""),
            access_token="",
            refresh_token="",
            id_token="",
        )
        assert config.auth_token_path
        with open(config.auth_token_path, "xb") as token_file:
            token_file.write(base64.b64encode(cache.model_dump_json().encode("utf-8")))

        client = BlueapiClient.from_config(config=config)
        patcher = mock.patch(
            "blueapi.service.authentication.SessionManager.get_valid_access_token",
            side_effect=get_access_token,
        )
        patcher.start()
        yield client
        patcher.stop()
    return BlueapiClient.from_config(config=config)
