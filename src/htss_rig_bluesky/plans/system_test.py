import bluesky.plans as bp
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.plan_stubs.data_session import attach_data_session_metadata_decorator
from ophyd_async.core import (
    StandardDetector,
    StandardFlyer,
)
from ophyd_async.epics.motor import Motor
from ophyd_async.fastcs.panda import (
    HDFPanda,
    StaticSeqTableTriggerLogic,
)
from ophyd_async.plan_stubs import ensure_connected, fly_and_collect
from ophyd_async.plan_stubs._fly import (
    prepare_static_seq_table_flyer_and_detectors_with_same_trigger,
)

# Plans utilized for system testing
# This module contains a collection of Bluesky plans designed for system testing.
# These plans are used to perform various types of scans and data collection routines
# using the Bluesky framework and ophyd_async devices. Each plan is decorated with
# metadata to attach data session information, ensuring that all collected data
# is properly annotated and organized.


@attach_data_session_metadata_decorator()
def fly_and_collect_plan(panda: HDFPanda, diff: StandardDetector) -> MsgGenerator:
    trigger_logic = StaticSeqTableTriggerLogic(panda.seq[1])

    flyer = StandardFlyer(
        trigger_logic,
        name="flyer",
    )
    yield from ensure_connected(diff, panda, flyer)

    @bpp.stage_decorator(devices=[diff, panda, flyer])
    @bpp.run_decorator()
    def inner():
        yield from prepare_static_seq_table_flyer_and_detectors_with_same_trigger(
            flyer, [diff], number_of_frames=15, exposure=0.1, shutter_time=0.05
        )
        yield from fly_and_collect(
            stream_name="primary",
            flyer=flyer,
            detectors=[diff],
        )

    yield from inner()


@attach_data_session_metadata_decorator()
def step_scan_plan(detectors: StandardDetector, motor: Motor) -> MsgGenerator:
    yield from bp.scan([detectors], motor, -15, 15, num=10)


@attach_data_session_metadata_decorator()
def log_scan_plan(detectors: StandardDetector, motor: Motor) -> MsgGenerator:
    yield from bp.log_scan(
        detectors=[detectors], motor=motor, start=1, stop=100, num=10
    )
