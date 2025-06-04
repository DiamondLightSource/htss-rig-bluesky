import pytest
from blueapi.client.client import BlueapiClient
from blueapi.config import ApplicationConfig, RestConfig, StompConfig
from blueapi.worker.task import Task
from bluesky_stomp.models import BasicAuthentication

from htss_rig_bluesky.names import BEAMLINE


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
def config() -> ApplicationConfig:
    if BEAMLINE == "p46":
        return ApplicationConfig(
            stomp=StompConfig(
                enabled=True,
                host="172.23.168.212",
                auth=BasicAuthentication(username="guest", password="guest"),  # type: ignore
            ),
            api=RestConfig(
                host="p46-blueapi.diamond.ac.uk", port=443, protocol="https"
            ),
        )
    else:
        return ApplicationConfig(
            stomp=StompConfig(
                enabled=True,
                host="localhost",
                auth=BasicAuthentication(username="guest", password="guest"),  # type: ignore
            )
        )


# This client will use authentication if a valid cached token is found
@pytest.fixture
def client(config: ApplicationConfig) -> BlueapiClient:
    return BlueapiClient.from_config(config=config)
