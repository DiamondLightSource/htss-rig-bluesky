from dodal.devices.areadetector import AdAravisDetector
from ophyd import Component, EpicsMotor, MotorBundle

from .names import pv_prefix


class SampleStage(MotorBundle):
    x: EpicsMotor = Component(EpicsMotor, "X")
    theta: EpicsMotor = Component(EpicsMotor, "A")


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
