#
# The following set of plans may be used as system tests to "exercise" the rigs
#


from collections.abc import Generator

import bluesky.plan_stubs as bps
import bluesky.plans as bp
import bluesky.preprocessors as bpp
from bluesky.protocols import Status
from bluesky.utils import MsgGenerator
from ophyd_async.epics.adaravis import AravisDetector
from ophyd_async.epics.motor import Motor


def exercise_detector(det: AravisDetector) -> Generator:
    """
    exercise the detector by taking a frame.

    Args:
        det: Detector

    Yields:
        Plan
    """

    yield from bp.count([det])


def exercise_motor(motor: Motor) -> Generator:
    """
    Exercise a motor by making sure it can traverse between a low point
    and a high point.

    Args:
        motor: The motor

    Yields:
        Plan
    """

    low_limit, high_limit = yield from get_limits(motor, padding=0.2)

    @bpp.run_decorator()
    @bpp.stage_decorator([motor])
    def move_and_monitor():
        status: Status = yield from bps.abs_set(
            motor,
            high_limit,
            wait=False,
            group=move_and_monitor.__name__,
        )
        while not status.done:
            yield from bps.trigger_and_read([motor])
            yield from bps.sleep(0.1)
        yield from bps.wait(group=move_and_monitor.__name__)

    # Perform plan as max velocity
    max_velocity = yield from bps.rd(motor.velocity)
    yield from bps.abs_set(motor.velocity, max_velocity)

    # Move to start point
    yield from bps.abs_set(motor, low_limit, wait=True)

    # Traverse to high limit, taking a snapshot of motor's position at 10Hz
    yield from move_and_monitor()


def get_limits(motor: Motor, padding: float = 0.0) -> MsgGenerator[tuple[float, float]]:
    low_limit = yield from bps.rd(motor.low_limit_travel)
    high_limit = yield from bps.rd(motor.high_limit_travel)
    return low_limit + padding, high_limit - padding
