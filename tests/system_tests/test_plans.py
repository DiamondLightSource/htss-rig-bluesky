import tempfile
from dataclasses import dataclass

import pytest
from blueapi.client.client import BlueapiClient
from blueapi.client.event_bus import AnyEvent
from blueapi.core.bluesky_types import DataEvent
from blueapi.worker.event import TaskStatus, WorkerEvent, WorkerState
from blueapi.worker.task import Task


# Please export BEAMLINE=pXX before running the tests or add it in pyproject.toml
@pytest.fixture
def tiled_client():
    from tiled.catalog import in_memory
    from tiled.client import Context, from_context
    from tiled.server.app import build_app

    with tempfile.TemporaryDirectory() as tempdir:
        catalog = in_memory(writable_storage=tempdir, readable_storage=None)
        app = build_app(catalog)
        with Context.from_app(app) as context:
            client = from_context(context)
            yield client


@pytest.mark.parametrize("device", ["sample_stage", "panda", "det"])
def test_device_present(client: BlueapiClient, device: str):
    assert client.get_device(device), f"{device} is not available"


@pytest.mark.parametrize("motor", ["sample_stage.x", "sample_stage.theta"])
def test_motor_behavoir(client: BlueapiClient, motor: str):
    task = Task(name="exercise_motor", params={"motor": motor})
    r = run_plan_test(client, task)
    tiled = r.tiled()
    print(tiled)


@pytest.mark.parametrize(
    "task",
    [
        Task(
            name="step_scan_plan",
            params={
                "detectors": "det",
                "motor": "sample_stage.theta",
            },
        ),
        Task(
            name="fly_and_collect_plan",
            params={
                "panda": "panda",
                "diff": "det",
            },
        ),
        Task(
            name="log_scan_plan",
            params={
                "detectors": "det",
                "motor": "sample_stage.x",
            },
        ),
    ],
)
def test_scan(
    client: BlueapiClient,
    task: Task,
):
    result = run_plan_test(client, task)

    assert result.complete_without_errors()
    assert result.worker_idle_at_end()
    assert result.worker_start_and_stop()


@dataclass(frozen=True)
class PlanTestResult:
    all_events: list[AnyEvent]
    task_id: str

    def tiled(self):
        client = tiled_client()
        for data_event in self.data_events():
            client.send(data_event.model_d)
        return client

    def worker_idle_at_end(self) -> bool:
        return self.final_event().state is WorkerState.IDLE

    def worker_start_and_stop(self) -> bool:
        # First event is WorkerEvent
        assert self.all_events[0] == WorkerEvent(
            state=WorkerState.RUNNING,
            task_status=TaskStatus(
                task_id=self.task_id(),
                task_complete=False,
                task_failed=False,
            ),
        )

        # Last 2 events are WorkerEvent
        assert self.all_events[-2:] == [
            WorkerEvent(
                state=WorkerState.IDLE,
                task_status=TaskStatus(
                    task_id=self.task_id(),
                    task_complete=False,
                    task_failed=False,
                ),
            ),
            WorkerEvent(
                state=WorkerState.IDLE,
                task_status=TaskStatus(
                    task_id=self.task_id(),
                    task_complete=True,
                    task_failed=False,
                ),
            ),
        ]

    def complete_without_errors(self) -> bool:
        final_event = self.final_event()
        return final_event.is_complete() and not final_event.is_error()

    def task_id(self) -> str:
        return self.final_event().task_status.task_id

    def final_event(self) -> WorkerEvent:
        event = self.all_events[-1]
        assert isinstance(event, WorkerEvent)
        return event

    def data_events(self) -> list[DataEvent]:
        return [event for event in self.all_events if isinstance(event, DataEvent)]


def run_plan_test(client: BlueapiClient, task: Task) -> PlanTestResult:
    all_events: list[AnyEvent] = []

    def on_event(event: AnyEvent):
        all_events.append(event)

    final_event = client.run_task(task, on_event=on_event)
    assert final_event == all_events[-1]
    return PlanTestResult(all_events=all_events)
