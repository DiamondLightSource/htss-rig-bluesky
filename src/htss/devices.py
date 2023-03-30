import os

from dodal.devices.areadetector import AdAravisDetector
from ophyd import Component, EpicsMotor, MotorBundle

from .names import pv_prefix


class SampleStage(MotorBundle):
    x: EpicsMotor = Component(EpicsMotor, "X")
    theta: EpicsMotor = Component(EpicsMotor, "A")


def sample(name: str = "sample_stage") -> SampleStage:
    return SampleStage(name=name, prefix=f"{pv_prefix()}-MO-MAP-01:STAGE:")


def det(name: str = "det") -> AdAravisDetector:
    det = AdAravisDetector(name=name, prefix=f"{pv_prefix()}-EA-DET-01:")
    det.hdf.reg_root = "/exports/mybeamline/data"
    det.hdf.write_path_template = "%Y"
    return det
