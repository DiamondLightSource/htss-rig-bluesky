from typing import Generator, Optional

import bluesky.plan_stubs as bps
import bluesky.plans as bp
from ophyd import pv_positioner

from htss.devices import AdAravisDetector, SampleStage


def scan_centre(
    det: AdAravisDetector,
    sample: SampleStage,
    min_x: Optional[float] = None,
    max_x: Optional[float] = None,
    x_steps: int = 10,
) -> Generator:
    x_range = abs(sample.x.high_limit - sample.x.low_limit)
    limit_margin = x_range * 0.01
    min_x = min_x or sample.x.low_limit + limit_margin
    max_x = max_x or sample.x.high_limit - limit_margin

    yield from bps.mv(sample.theta, 0.0)
    yield from bp.scan([det], sample.x, min_x, max_x, x_steps)


def scan_exposure(
    det: AdAravisDetector,
    min_exposure: float = 0.01,
    max_exposure: float = 0.2,
    exposure_steps: int = 10,
) -> Generator:
    exposure_time = det.cam.acquire_time
    yield from bps.abs_set(det.cam.acquire_period, max_exposure + 0.1)
    yield from bp.scan(
        [det],
        exposure_time,
        min_exposure,
        max_exposure,
        exposure_steps,
    )
