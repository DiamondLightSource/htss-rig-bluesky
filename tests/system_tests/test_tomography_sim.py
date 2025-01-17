from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from bluesky.run_engine import RunEngine
from ophyd_async.core import DeviceCollector
from ophyd_async.sim.demo import PatternDetector, SimMotor

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
def x(run_engine: RunEngine) -> SimMotor:
    with DeviceCollector():
        x = SimMotor()
    return x


@pytest.fixture
def theta(run_engine: RunEngine) -> SimMotor:
    with DeviceCollector():
        theta = SimMotor()
    return theta


@pytest.fixture
def beam(run_engine: RunEngine) -> SimMotor:
    with DeviceCollector():
        beam = SimMotor()
    return beam


@pytest.fixture
def det(
    run_engine: RunEngine,
    data_dir: Path,
    x: SimMotor,
    theta: SimMotor,
    beam: SimMotor,
) -> PatternDetector:
    with DeviceCollector(mock=True):
        det = PatternDetector(path=data_dir, name="det")
    return det


def test_tomography(
    run_engine: RunEngine,
    det: PatternDetector,
    x: SimMotor,
    theta: SimMotor,
    beam: SimMotor,
) -> None:
    spec = TomographySpec.default()
    plan = tomography_step_scan([x], beam, x, theta, spec)
    run_engine(plan)
