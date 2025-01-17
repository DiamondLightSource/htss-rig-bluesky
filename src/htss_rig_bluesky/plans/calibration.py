
import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.beamlines.training_rig import TrainingRigSampleStage as SampleStage
from dodal.plans import spec_scan
from ophyd_async.epics.adaravis import AravisDetector
from scanspec.specs import Line


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
) -> MsgGenerator:
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
    high = yield from bps.rd(sample.x.high_limit_travel)
    low = yield from bps.rd(sample.x.low_limit_travel)

    x_range = abs(high - low)
    limit_margin = x_range * 0.01
    min_x = min_x or low + limit_margin
    max_x = max_x or high - limit_margin

    yield from bps.mv(
        det.drv.num_images,
        images_per_side,
        det.drv.acquire_time,
        exposure_time,
    )
    yield from spec_scan(
        [det],
        Line(sample.x, min_x, max_x, x_steps)
        * ~Line(sample.theta, one_side, other_side, 2),
    )


def scan_exposure(
    det: AravisDetector,
    min_exposure: float = 0.01,
    max_exposure: float = 0.2,
    exposure_steps: int = 10,
) -> MsgGenerator:
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
    # Make sure the camera always leaves enough deadtime so frames do not overlap
    # This can be optmised further in the future
    deadtime = det.controller.get_deadtime(max_exposure)
    yield from bps.abs_set(det.drv.acquire_period, max_exposure + deadtime)

    # Scan in exposure time
    yield from spec_scan(
        [det],
        Line(
            det.drv.acquire_time,
            min_exposure,
            max_exposure,
            exposure_steps,
        ),
    )
