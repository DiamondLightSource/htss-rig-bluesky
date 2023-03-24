#
# The following set of plans may be used as system tests to "exercise" the rigs
#


from typing import Generator

import bluesky.plan_stubs as bps
import bluesky.plans as bp
from ophyd import PositionerBase

from htss.devices import AdAravisDetector, SampleStage


def excercise_beamline(det: AdAravisDetector, sample: SampleStage) -> Generator:
    yield from excercise_motors(sample)
    yield from excercise_detector(det)
    yield from exercise_scan(det, sample)


def excercise_motors(sample: SampleStage) -> Generator:
    yield from excercise_motor(sample.x, -24.9, 14.0, tolerance=0.1)
    yield from excercise_motor(
        sample.theta, -1000.0, 1000.0, tolerance=0.1, check_limits=False
    )


def excercise_detector(det: AdAravisDetector) -> Generator:
    print(f"Excercising {det}")
    yield from ensure_detector_ready(det)
    yield from bp.count([det])


def exercise_scan(det: AdAravisDetector, sample: SampleStage) -> Generator:
    print("Excercising scan")
    yield from ensure_detector_ready(det)
    yield from bp.scan([det], sample.theta, -180.0, 180.0, 10)


def ensure_detector_ready(det: AdAravisDetector) -> Generator:
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


def excercise_motor(
    motor: PositionerBase,
    low_limit: float,
    high_limit: float,
    tolerance: float = 0.0,
    check_limits: bool = True,
) -> Generator:
    name = motor.name
    print(f"Excercising {name}")

    if check_limits:
        assert_limits_within(motor, low_limit, high_limit)
    yield from bps.mv(motor, low_limit, wait=True)
    yield from assert_motor_at(motor, low_limit, tolerance)
    yield from bps.mv(motor, high_limit, wait=True)
    yield from assert_motor_at(motor, high_limit, tolerance)


def assert_limits_within(
    motor: PositionerBase, low_limit: float, high_limit: float
) -> None:
    name = motor.name
    assert (
        motor.high_limit >= high_limit
    ), f"{name}'s upper limit is {motor.high_limit}, should be >= {high_limit}"
    assert (
        motor.low_limit <= low_limit
    ), f"{name}'s lower limit is {motor.low_limit}, should be <= {low_limit}"


def assert_motor_at(
    motor: PositionerBase, pos: float, tolerance: float = 0.0
) -> Generator:
    actual_pos = yield from bps.rd(motor)
    upper_bound = pos + (tolerance / 2.0)
    lower_bound = pos - (tolerance / 2.0)
    assert (
        upper_bound >= actual_pos >= lower_bound
    ), f"{motor.name} is at {actual_pos}, should be between {lower_bound} and {upper_bound}"
