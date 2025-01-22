import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.plans.scanspec import spec_scan
from dodal.plans.wrapped import count
from ophyd_async.epics.adaravis import AravisDetector
from ophyd_async.epics.motor import Motor
from scanspec.specs import Line
import logging

from ophyd_async.fastcs.panda import HDFPanda
from pathlib import Path
from dodal.beamlines.training_rig import TrainingRigSampleStage

def step_scan_diagnostic(detector: AravisDetector, panda: HDFPanda, sample_stage: TrainingRigSampleStage) -> MsgGenerator:
    scanspec = Line(sample_stage.x, 0, 10, 10) * ~Line(sample_stage.theta, 0, 360, 4)
    yield from spec_scan([detector], scanspec)

def detector_diagnostic(detector: AravisDetector) -> MsgGenerator:
    diagnostic_fields = {component for _, component in detector.drv.children()}.union(
        {component for _, component in detector.hdf.children()}
    )

    yield from bps.abs_set(
        detector.drv.acquire_time,
        0.1,
        wait=False,
        group="setup",
    )
    yield from bps.abs_set(
        detector.drv.acquire_period,
        detector.controller.get_deadtime(0.1),
        wait=False,
        group="setup",
    )
    yield from bps.abs_set(
        detector.drv.num_images,
        1,
        wait=False,
        group="setup",
    )
    yield from bps.wait(group="setup")

    for i in [1, 10, 100, 100, 100, 1000]:
        yield from bpp.monitor_during_wrapper(
            count([detector], num=i), diagnostic_fields
        )


def motor_diagnostic(motor: Motor) -> MsgGenerator:
    initial_velocity = yield from bps.rd(motor.velocity)
    try:
        max_velocity = yield from bps.rd(motor.max_velocity)
        low_limit, high_limit = yield from padded_limits(motor)

        logging.info(f"Moving {motor.name} between {low_limit} and {high_limit} at up to {max_velocity}")

        diagnostic_fields = {
            motor.acceleration_time,
            motor.velocity,
            motor.max_velocity,
            motor.high_limit_travel,
            motor.low_limit_travel,
            motor.user_readback,
            motor.user_setpoint,
        }

        scanspec = Line(motor.velocity, max_velocity / 10.0, max_velocity, 5) * ~Line(
            motor, low_limit, high_limit, 2
        )

        # Drive the motor back and forth at different velocities,
        # monitoring paramters asynchronously
        yield from bpp.monitor_during_wrapper(
            spec_scan(diagnostic_fields, scanspec),
            diagnostic_fields,
        )
    finally:
        # Put veloicty back how we found it
        yield from bps.abs_set(motor.velocity, initial_velocity)


def padded_limits(
    motor: Motor, padding_percent: float = 0.05
) -> MsgGenerator[tuple[float, float]]:
    high_limit_travel = yield from bps.rd(motor.high_limit_travel)
    low_limit_travel = yield from bps.rd(motor.low_limit_travel)

    return low_limit_travel + abs(
        low_limit_travel * padding_percent
    ), high_limit_travel - abs(high_limit_travel * padding_percent)
