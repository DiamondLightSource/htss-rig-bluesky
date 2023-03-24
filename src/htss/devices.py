import os

from dodal.devices.areadetector import AdAravisDetector
from ophyd import Component, EpicsMotor, MotorBundle

BEAMLINE = os.environ.get("BEAMLINE", "")


class SampleStage(MotorBundle):
    x: EpicsMotor = Component(EpicsMotor, "X")
    theta: EpicsMotor = Component(EpicsMotor, "A")


def sample(name: str = "sample_stage") -> SampleStage:
    return SampleStage(name=name, prefix=f"{_prefix()}-MO-MAP-01:STAGE:")


def det(name: str = "det") -> AdAravisDetector:
    det = AdAravisDetector(name=name, prefix=f"{_prefix()}-EA-DET-01:")
    det.hdf.reg_root = "/exports/mybeamline/data"
    det.hdf.write_path_template = "%Y"
    return det


def _prefix() -> str:
    prefixes = {"p46": "BL46P", "p47": "BL47P", "p48": "BL46P", "p49": "BL49P"}
    beamline = BEAMLINE.lower()
    if beamline not in prefixes.keys():
        raise KeyError(f"Please set $BEAMLINE to one of {list(prefixes.keys())}")
    return prefixes[beamline]
