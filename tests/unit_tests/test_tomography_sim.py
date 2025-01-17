import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines.training_rig import det, sample_stage
from dodal.common.beamlines.beamline_utils import set_path_provider
from dodal.common.visit import LocalDirectoryServiceClient, StaticVisitPathProvider
from dodal.devices.training_rig.sample_stage import TrainingRigSampleStage
from ophyd_async.core import DeviceCollector
from ophyd_async.epics.adaravis import AravisDetector
from ophyd_async.epics.motor import Motor
from ophyd_async.sim.demo import SimMotor
from ophyd_async.testing import callback_on_mock_put, set_mock_value

from htss_rig_bluesky.models import TomographySpec
from htss_rig_bluesky.plans.tomography import tomography_step_scan


@pytest.fixture
def run_engine() -> RunEngine:
    return RunEngine()


@pytest.fixture
def data_dir() -> Path:
    d = TemporaryDirectory()
    yield Path(d.name)
    d.cleanup()


@pytest.fixture
def htss_sample_stage(run_engine: RunEngine) -> TrainingRigSampleStage:
    s = sample_stage(connect_immediately=True, mock=True)
    mock_motor_behavoir(s.x)
    mock_motor_behavoir(s.theta)
    return s


@pytest.fixture
def htss_det(
    run_engine: RunEngine,
    data_dir: Path,
    htss_sample_stage: TrainingRigSampleStage,
    beam: SimMotor,
) -> AravisDetector:
    set_path_provider(
        StaticVisitPathProvider(
            "p46",
            data_dir,
            client=LocalDirectoryServiceClient(),
        ),
    )

    d = det(connect_immediately=True, mock=True)
    mock_detector_behavoir(d, htss_sample_stage, beam)
    return d


@pytest.fixture
def beam(run_engine: RunEngine) -> SimMotor:
    with DeviceCollector():
        beam = SimMotor()
    return beam


def mock_motor_behavoir(motor: Motor) -> None:
    def propagate(value: float, wait: bool) -> None:
        set_mock_value(motor.user_readback, value)

    set_mock_value(motor.max_velocity, 1.0)
    set_mock_value(motor.velocity, 1.0)
    callback_on_mock_put(motor.user_setpoint, propagate)


def mock_detector_behavoir(
    detector: AravisDetector,
    sample: TrainingRigSampleStage,
    beam: SimMotor,
) -> None:
    async def mock_acquisition() -> None:
        num_images = await detector.drv.num_images.get_value()
        set_mock_value(detector.hdf.num_capture, num_images)

        # print(f"NIM: {num_images}")
        for i in range(1, num_images + 1):
            set_mock_value(detector.hdf.num_captured, i)
            # print(f"CAP <- {i}")
        set_mock_value(detector.hdf.num_captured, 0)

    async def on_acquire(acquire: bool, wait: bool) -> None:
        # print(f"ACQ: {acquire}")
        if acquire:
            asyncio.create_task(mock_acquisition())

    set_mock_value(detector.hdf.file_path_exists, True)
    callback_on_mock_put(detector.drv.acquire, on_acquire)


# def test_count(
#     run_engine: RunEngine,
#     htss_det: AravisDetector,
# ) -> None:
#     plan = count([htss_det], num=5)
#     run_engine(plan)


def test_tomography(
    run_engine: RunEngine,
    htss_det: AravisDetector,
    htss_sample_stage: TrainingRigSampleStage,
    beam: SimMotor,
) -> None:
    spec = TomographySpec.default()
    plan = tomography_step_scan(
        [htss_det],
        beam,
        htss_sample_stage.x,
        htss_sample_stage.theta,
        spec,
    )
    run_engine(plan)
