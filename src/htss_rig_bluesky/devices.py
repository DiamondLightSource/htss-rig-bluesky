from enum import Enum
from pathlib import Path

import epics
from ophyd_async.core import (
    AsyncStatus,
    AutoIncrementFilenameProvider,
    Device,
    StaticPathProvider,
)
from ophyd_async.epics.areadetector.aravis import AravisDetector
from ophyd_async.epics.motion import Motor
from ophyd_async.epics.signal import epics_signal_rw

from .names import pv_prefix


class SampleStage(Device):
    def __init__(self, prefix: str, name: str):
        self.x = Motor(prefix + "X")
        self.theta = Motor(prefix + "A")
        super().__init__(name)


class BacklightPower(str, Enum):
    ON = "On"
    OFF = "Off"


class Backlight(Device):
    def __init__(self, prefix: str, name: str = ""):
        self.power = epics_signal_rw(BacklightPower, prefix + "State")
        super().__init__(name)

    @AsyncStatus.wrap
    async def set(self, position: BacklightPower):
        """This setter will turn the backlight on when we move it in to the beam and off
        when we move it out."""
        await self.power.set(position)


def sample(name: str = "sample_stage") -> SampleStage:
    """
    Create sample stage ophyd-async device

    Args:
        name: Name for this device for reference in events.
            Defaults to "sample_stage".

    Returns:
        SampleStage: A new ophyd-async Device
    """

    return SampleStage(name=name, prefix=f"{pv_prefix()}-MO-MAP-01:STAGE:")


def det(name: str = "det") -> AravisDetector:
    """
    Create detector stage ophyd-async device

    Args:
        name: Name for this device for reference in events.
            Defaults to "det".

    Returns:
        AravisDetector: A new ophyd-async Device
    """

    dir_prov = StaticPathProvider(
        AutoIncrementFilenameProvider(),
        Path("/exports/mybeamline/data"),
    )
    return AravisDetector(
        name=name,
        prefix=f"{pv_prefix()}-EA-DET-01:",
        path_provider=dir_prov,
        hdf_suffix="HDF5:",
        drv_suffix="DET:",
    )


def beam(name: str = "beam") -> Backlight:
    """
    Create an object to represent the beam

    Args:
        name: Name for this device for reference in events.
            Defaults to "beam".

    Backlight:
        Backlight: A new ophyd-async Device
    """

    return Backlight(name=name, prefix=f"{pv_prefix()}-EA-BEAM-01:")


def suppress_epics_warnings() -> None:
    def handle_messages(text): ...

    epics.ca.replace_printf_handler(handle_messages)
