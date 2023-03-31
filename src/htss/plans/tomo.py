from typing import Any, Dict, Generator, Optional

import bluesky.plan_stubs as bps
import bluesky.plans as bp
from ophyd import pv_positioner

from htss.devices import AdAravisDetector, SampleStage


def tomo_scan(
    det: AdAravisDetector,
    sample: SampleStage,
    exposure_time: float = 0.03,
    min_theta: float = 180.0,
    max_theta: float = 0.0,
    theta_steps: int = 90,
    beam_centre: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Generator:
    metadata = {
        "exposure_time": exposure_time,
        "min_theta": min_theta,
        "max_theta": max_theta,
        "theta_steps": theta_steps,
        "beam_centre": beam_centre,
        **(metadata or {}),
    }
    if beam_centre is not None:
        yield from bps.mv(sample.x, beam_centre)
    yield from bps.abs_set(det.cam.acquire_time, exposure_time)
    yield from bp.scan(
        [det, sample.x], sample.theta, min_theta, max_theta, theta_steps, md=metadata
    )
