import asyncio
from collections.abc import Generator
from typing import Any, TypeAlias

import bluesky.plan_stubs as bps
import bluesky.plans as bp
from ophyd_async.epics.adaravis import AravisDetector

SampleStage: TypeAlias = Any


def scan_center(
    det: AravisDetector,
    sample: SampleStage,
    min_x: float | None = None,
    max_x: float | None = None,
    x_steps: int = 20,
    one_side: float = 0.0,
    other_side: float = 180.0,
    images_per_side: int = 5,
    exposure_time: float = 0.15,
) -> Generator:
    """
    Scan the sample x motor across a range of positions.
    For each x position, the sample will be imaged from two angles, typically 180
    degrees apart. It may also be imaged several times from each position to average
    out noise.

    The data from this plan is useful for calibrating the sample, performing sum and
    centroid post-processing on the data can be used to find where to put x such that
    the sample is in the center of the beam.

    Args:
        det: The detector
        sample: The sample stage
        min_x: The x position to start with. Defaults to low limit of motor
        max_x: The x position to end with. Defaults to high limit of motor
        x_steps: The number of steps to take. Defaults to 10
        one_side: The position of theta representing a side of the sample
        other_side: Another theta position, typically 180 degrees away from one_side
        images_per_side: Number of images to take of each side at each x position
        exposure_time: Exposure time of the detector

    Yields:
        Plan
    """
    limits = asyncio.gather(
        sample.x.high_limit_travel.get_value(), sample.x.low_limit_travel.get_value()
    )
    high, low = limits.result()
    x_range = abs(high - low)
    limit_margin = x_range * 0.01
    min_x = min_x or low + limit_margin
    max_x = max_x or high - limit_margin

    yield from bps.mv(
        det.driver.num_images,
        images_per_side,
        det.driver.acquire_time,
        exposure_time,
    )
    yield from bp.grid_scan(
        [det],
        sample.x,
        min_x,
        max_x,
        x_steps,
        sample.theta,
        one_side,
        other_side,
        2,
        snake_axes=True,
    )


def scan_exposure(
    det: AravisDetector,
    min_exposure: float = 0.01,
    max_exposure: float = 0.2,
    exposure_steps: int = 10,
) -> Generator:
    """
    Take images at a range of exposure times

    Args:
        det: The detector
        min_exposure: The exposure time to start with. Defaults to 0.01 seconds
        max_exposure: The exposure time to end with. Defaults to 0.2 seconds
        exposure_steps: The number of steps to take. Defaults to 10

    Yields:
        Plan
    """
    exposure_time = det.driver.acquire_time
    yield from bps.abs_set(det.driver.acquire_period, max_exposure + 0.1)
    yield from bp.scan(
        [det],
        exposure_time,
        min_exposure,
        max_exposure,
        exposure_steps,
    )
