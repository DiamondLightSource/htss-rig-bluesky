import epics
from bluesky.protocols import Status
from dodal.devices.areadetector import AdAravisDetector
from ophyd import Component, Device, EpicsMotor, EpicsSignalWithRBV, MotorBundle

from .names import pv_prefix


class SampleStage(MotorBundle):
    x: EpicsMotor = Component(EpicsMotor, "X")
    theta: EpicsMotor = Component(EpicsMotor, "A")


class Backlight(Device):
    on: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "State")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on.put_complete = True

    def set(self, value) -> Status:
        return self.on.set(value)


def sample(name: str = "sample_stage") -> SampleStage:
    """
    Create sample stage Ophyd device

    Args:
        name: Name for this device for reference in events.
            Defaults to "sample_stage".

    Returns:
        SampleStage: A new Ophyd Device
    """

    return SampleStage(name=name, prefix=f"{pv_prefix()}-MO-MAP-01:STAGE:")


def det(name: str = "det") -> AdAravisDetector:
    """
    Create detector stage Ophyd device

    Args:
        name: Name for this device for reference in events.
            Defaults to "det".

    Returns:
        SampleStage: A new Ophyd Device
    """

    det = AdAravisDetector(name=name, prefix=f"{pv_prefix()}-EA-DET-01:")
    det.read_attrs += ["cam"]
    det.cam.read_attrs += ["acquire_time", "acquire_period"]
    det.hdf.reg_root = "/exports/mybeamline/data"
    det.hdf.write_path_template = "%Y"
    return det


def beam(name: str = "beam") -> Backlight:
    """
    Create an object to represent the beam

    Args:
        name: Name for this device for reference in events.
            Defaults to "beam".

    Backlight:
        SampleStage: A new Ophyd Device
    """

    return Backlight(name=name, prefix=f"{pv_prefix()}-EA-BEAM-01:")


def suppress_epics_warnings() -> None:
    def handle_messages(text):
        ...

    epics.ca.replace_printf_handler(handle_messages)
