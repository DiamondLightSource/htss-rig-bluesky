#
# The following set of plans may be used as system tests to "exercise" the rigs
#


from collections.abc import Generator
from typing import Any, TypeAlias

import bluesky.plan_stubs as bps
import bluesky.plans as bp
from ophyd_async.epics.adaravis import AravisDetector
from ophyd_async.epics.motor import Motor

from .detector import ensure_detector_ready

SampleStage: TypeAlias = Any


def exercise_beamline(det: AravisDetector, sample: SampleStage) -> Generator:
    """
    Perform all beamline exercise plans sequentially.

    Args:
        det: Detector
        sample: Sample stage

    Yields:
        Plan
    """

    yield from exercise_motors(sample)
    yield from exercise_detector(det)
    yield from exercise_scan(det, sample)


def exercise_motors(sample: SampleStage) -> Generator:
    """
    exercise the motors on the sample stage.

    Args:
        sample: Sample stage

    Yields:
        Plan
    """

    yield from exercise_motor(sample.x, -24.9, 14.0, tolerance=0.1)
    yield from exercise_motor(
        sample.theta, -1000.0, 1000.0, tolerance=0.1, check_limits=False
    )


def exercise_detector(det: AravisDetector) -> Generator:
    """
    exercise the detector by taking a frame.

    Args:
        det: Detector

    Yields:
        Plan
    """

    print(f"Excercising {det}")
    yield from ensure_detector_ready(det)
    yield from bp.count([det])


def exercise_scan(det: AravisDetector, sample: SampleStage) -> Generator:
    """
    Perform a short scan to exercise the test rig.

    Args:
        det (AravisDetector): Detector
        sample (SampleStage): Sample stage

    Yields:
        Plan
    """

    print("Excercising scan")
    yield from ensure_detector_ready(det)
    yield from bp.scan([det], sample.theta, -180.0, 180.0, 10)


def exercise_motor(
    motor: Motor,
    low_limit: float,
    high_limit: float,
    tolerance: float = 0.0,
    check_limits: bool = True,
) -> Generator:
    """
    exercise a motor by making sure it can traverse between a low point
    and a high point.

    Args:
        motor: The motor
        low_limit: Place to start
        high_limit: Place to end
        tolerance: Tolerance for checking motor position. Defaults to 0.0.
        check_limits: Check whether the motor's limits fall within the bounds,
            disable for limitless motors. Defaults to True.

    Yields:
        Plan
    """

    name = motor.name
    print(f"Excercising {name}")

    if check_limits:
        yield from assert_limits_within(motor, low_limit, high_limit)
    yield from bps.abs_set(motor, low_limit, wait=True)
    yield from assert_motor_at(motor, low_limit, tolerance)
    yield from bps.abs_set(motor, high_limit, wait=True)
    yield from assert_motor_at(motor, high_limit, tolerance)


def assert_limits_within(
    motor: Motor, low_limit: float, high_limit: float
) -> Generator:
    """
    Check a motors limits fall within the bounds supplied.
    Note this is not an exact check, just whether the real limits exceed
    the "limit limits" supplied.

    Args:
        motor: The motor with limits
        low_limit: The lower bound
        high_limit: The upper bound
    """

    name = motor.name
    motor_high_limit: float = yield from bps.rd(motor.high_limit_travel)
    motor_low_limit: float = yield from bps.rd(motor.low_limit_travel)
    assert motor_high_limit >= high_limit, (
        f"{name}'s upper limit is {motor.high_limit_travel}, should be >= {high_limit}"
    )
    assert motor_low_limit <= low_limit, (
        f"{name}'s lower limit is {motor_low_limit}, should be <= {low_limit}"
    )


def assert_motor_at(motor: Motor, pos: float, tolerance: float = 0.0) -> Generator:
    """
    Check a motor has reached a required position

    Args:
        motor: The motor to check
        pos: The required position
        tolerance: Plus or minus tolerance, useful for
            less precise motors. Defaults to 0.0.

    Yields:
        Plan
    """

    actual_pos = yield from bps.rd(motor)
    upper_bound = pos + (tolerance / 2.0)
    lower_bound = pos - (tolerance / 2.0)
    assert upper_bound >= actual_pos >= lower_bound, (
        f"{motor.name} is at {actual_pos}, "
    )
    f"should be between {lower_bound} and {upper_bound}"
