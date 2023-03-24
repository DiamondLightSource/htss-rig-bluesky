#
# The following set of plans may be used as system tests to "exercise" the rigs
#


from typing import Any, Callable, Generator, Optional

import bluesky.plan_stubs as bps
from bluesky import RunEngine
from ophyd import PositionerBase

from htss.devices import AdAravisDetector, SampleStage


def excercise_beamline(det: AdAravisDetector, sample: SampleStage) -> Generator:
    yield from excercise_motors(sample)


def excercise_motors(sample: SampleStage) -> Generator:
    yield from excercise_motor(sample.x, -24.9, 14.0, tolerance=0.1)
    yield from excercise_motor(
        sample.theta, -1000.0, 1000.0, tolerance=0.1, check_limits=False
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
