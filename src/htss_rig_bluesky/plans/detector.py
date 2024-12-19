from collections.abc import Generator
from dataclasses import dataclass

import bluesky.plan_stubs as bps
from ophyd_async.epics.adaravis import AravisDetector


@dataclass
class Roi:
    min_x: int
    min_y: int
    size_x: int | None = None
    size_y: int | None = None

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


def ensure_detector_ready(det: AravisDetector) -> Generator:
    """
    Setup detector for exercises

    Args:
        det: Detector

    Yields:
        Plan
    """
    # TODO: need num exposures too?
    yield from bps.mv(
        det.drv.num_images,
        1,
        det.drv.acquire_period,
        0.1,
        det.drv.acquire_time,
        0.15,
        det.hdf.nd_array_port,
        "DET.CAM",
    )


def set_roi(det: AravisDetector, roi: Roi) -> Generator:
    """
    Setup detector ROI and frame size

    Args:
        det: Detector
        roi: ROI to take

    Yields:
        Plan
    """
    # Ophyd Async AravisDetector doesn't appear to have signal for max sizes
    # eg DET:MaxSizeX_RBVDET:MaxSizeX_RBV

    sets = {det.drv.array_size_x: roi.size_x, det.drv.array_size_y: roi.size_y}

    for signal, value in sets.items():
        yield from bps.abs_set(signal, value)

    # TODO: Must prime plugins before acquisition
