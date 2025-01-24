import pytest
from bluesky import RunEngine
from dodal.beamlines import training_rig as training_rig
from ophyd_async.core import (
    Device,
    DeviceVector,
)
from ophyd_async.epics.core import epics_signal_rw
from ophyd_async.fastcs.panda import HDFPanda
from ophyd_async.plan_stubs import ensure_connected

from htss_rig_bluesky.plans.backlight import (
    set_backlight_control_port,
    set_backlight_intensity,
)


@pytest.fixture
def run_engine() -> RunEngine:
    return RunEngine()


@pytest.fixture
async def mock_panda(
    run_engine: RunEngine,
):
    class TtlOutBlock(Device):
        def __init__(self, name: str = ""):
            self.val = epics_signal_rw(str, "VAL")
            super().__init__(name)

    mock_panda = training_rig.panda()
    mock_panda.phase_1_signal_units = epics_signal_rw(int, "")
    mock_panda.ttlout = DeviceVector({i: TtlOutBlock() for i in range(1, 5)})

    run_engine(ensure_connected(mock_panda, mock=True))
    yield mock_panda


async def test_set_control_port_sets_control_port(
    run_engine: RunEngine, mock_panda: HDFPanda
):
    assert (await mock_panda.ttlout[2].val.get_value()) == ""
    run_engine(set_backlight_control_port(mock_panda, "FOO"), wait=True)
    assert (await mock_panda.ttlout[2].val.get_value()) == "FOO"


@pytest.mark.parametrize("intensity,port_value", [(0.0, "ZERO"), (1.0, "ONE")])
async def test_constant_port_value(
    run_engine: RunEngine,
    mock_panda: HDFPanda,
    intensity: float,
    port_value: str,
):
    run_engine(set_backlight_intensity(mock_panda, intensity), wait=True)
    assert (await mock_panda.ttlout[2].val.get_value()) == port_value
