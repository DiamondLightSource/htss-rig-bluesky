from dataclasses import dataclass
from typing import Generator, Optional

import bluesky.plan_stubs as bps

from htss.devices import AdAravisDetector


@dataclass
class Roi:
    min_x: int
    min_y: int
    size_x: Optional[int] = None
    size_y: Optional[int] = None

    @classmethod
    def full_frame(cls) -> "Roi":
        return cls(0, 0)

    @classmethod
    def strip(cls) -> "Roi":
        return cls(0, 600, size_y=20)

    @property
    def max_x(self) -> int:
        return self.min_x + (self.size_x or 0)

    @property
    def max_y(self) -> int:
        return self.min_y + (self.size_y or 0)


def ensure_detector_ready(det: AdAravisDetector) -> Generator:
    """
    Setup detector for exercises

    Args:
        det: Detector

    Yields:
        Plan
    """

    yield from bps.mv(
        det.cam.num_exposures,
        1,
        det.cam.num_images,
        1,
        det.cam.acquire_period,
        0.1,
        det.cam.acquire_time,
        0.15,
    )


def set_roi(det: AdAravisDetector, roi: Roi) -> Generator:
    """
    Setup detector ROI and frame size

    Args:
        det: Detector
        roi: ROI to take

    Yields:
        Plan
    """

    max_x = yield from bps.rd(det.cam.max_size.max_size_x)
    max_y = yield from bps.rd(det.cam.max_size.max_size_y)

    sets = {
        det.cam.min_x: roi.min_x,
        det.cam.min_y: roi.min_y,
        det.cam.size.size_x: roi.size_x or max_x,
        det.cam.size.size_y: roi.size_y or max_y,
    }

    for signal, value in sets.items():
        yield from bps.abs_set(signal, value)

    # TODO: Must prime plugins before acquisition
