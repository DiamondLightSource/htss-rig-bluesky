import os

from dodal.devices.areadetector import AdAravisDetector
from ophyd import Component, EpicsMotor, MotorBundle

BEAMLINE = os.environ.get("BEAMLINE")
_PREFIXES = {"p46": "BL46P", "p47": "BL47P", "p48": "BL46P", "p49": "BL49P"}
if BEAMLINE not in _PREFIXES.keys():
    raise KeyError(f"Please set $BEAMLINE to one of {list(_PREFIXES.keys())}")
PREFIX = _PREFIXES[BEAMLINE.lower()]


class SampleStage(MotorBundle):
    x: EpicsMotor = Component(EpicsMotor, "X")
    theta: EpicsMotor = Component(EpicsMotor, "A")


def sample(name: str = "sample_stage") -> SampleStage:
    return SampleStage(name=name, prefix=f"{PREFIX}-MO-MAP-01:STAGE:")


def det(name: str = "det") -> AdAravisDetector:
    det = AdAravisDetector(name=name, prefix=f"{PREFIX}-EA-DET-01:")
    det.hdf.reg_root = "/scratch/mybeamline/data"
    det.hdf.write_path_template = "%Y"
    return det
