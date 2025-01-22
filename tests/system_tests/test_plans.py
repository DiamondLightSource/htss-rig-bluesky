import pytest
from blueapi.client.client import BlueapiClient
from blueapi.client.event_bus import AnyEvent
from blueapi.core.bluesky_types import DataEvent
from blueapi.worker.event import TaskStatus, WorkerEvent, WorkerState
from blueapi.worker.task import Task
from htss_rig_bluesky.plans.diagnostic import motor_diagnostic, detector_diagnostic, step_scan_diagnostic
# Please export BEAMLINE=pXX before running the tests or add it in pyproject.toml

TASKS = [
    Task(name=motor_diagnostic.__name__, params={
        "motor": "sample_stage.x"
    }),
    Task(name=motor_diagnostic.__name__, params={
        "motor": "sample_stage.theta"
    }),
    Task(name=detector_diagnostic.__name__, params={
        "detector": "det"
    }),
]

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
    "task", TASKS
)
def test_plan_runs(
    client: BlueapiClient,
    task: Task,
):
    assert client.get_plan(task.plan), f"In {task.plan} is not available"

    all_events: list[AnyEvent] = []

    def on_event(event: AnyEvent):
        all_events.append(event)

    client.run_task(task, on_event=on_event)

    _check_all_events(all_events)

    assert client.get_state() is WorkerState.IDLE
