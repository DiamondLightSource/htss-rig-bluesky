import pytest
from blueapi.client.client import BlueapiClient
from blueapi.client.event_bus import AnyEvent
from blueapi.core.bluesky_types import DataEvent
from blueapi.worker.event import TaskStatus, WorkerEvent, WorkerState
from blueapi.worker.task import Task

# System Test Instructions:
# 1. Set username, password, and beamline settings in conftest.py
#   (e.g., P46 beamline config provided).
# 2. Use the BEAMLINE variable to select the configuration:
#   - Export as an environment variable, or
#   - Define in pyproject.toml.
# 3. Login if BlueAPI server authentication is enabled.


def _check_all_events(all_events: list[AnyEvent]):
    assert (
        isinstance(all_events[0], WorkerEvent) and all_events[0].task_status is not None
    )
    task_id = all_events[0].task_status.task_id
    # First event is WorkerEvent
    assert all_events[0] == WorkerEvent(
        state=WorkerState.RUNNING,
        task_status=TaskStatus(
            task_id=task_id,
            task_complete=False,
            task_failed=False,
        ),
    )

    assert all(isinstance(event, DataEvent) for event in all_events[1:-2]), (
        "Middle elements must be DataEvents."
    )

    # Last 2 events are WorkerEvent
    assert all_events[-2:] == [
        WorkerEvent(
            state=WorkerState.IDLE,
            task_status=TaskStatus(
                task_id=task_id,
                task_complete=False,
                task_failed=False,
            ),
        ),
        WorkerEvent(
            state=WorkerState.IDLE,
            task_status=TaskStatus(
                task_id=task_id,
                task_complete=True,
                task_failed=False,
            ),
        ),
    ]


@pytest.mark.parametrize("device", ["sample_stage", "panda", "det"])
def test_device_present(client: BlueapiClient, device: str):
    assert client.get_device(device), f"{device} is not available"


@pytest.mark.parametrize(
    "plan", ["step_scan_plan", "fly_and_collect_plan", "log_scan_plan"]
)
def test_spec_scan_task(
    client: BlueapiClient,
    task_definition: dict[str, Task],
    plan: str,
):
    assert client.get_plan(plan), f"In {plan} is available"

    all_events: list[AnyEvent] = []

    def on_event(event: AnyEvent):
        all_events.append(event)

    client.run_task(task_definition[plan], on_event=on_event)

    _check_all_events(all_events)

    assert client.get_state() is WorkerState.IDLE
