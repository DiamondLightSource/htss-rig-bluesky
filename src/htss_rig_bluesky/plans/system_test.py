import bluesky.plan_stubs as bps
import bluesky.plans as bp
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator, short_uid
from dodal.plan_stubs.data_session import attach_data_session_metadata_decorator
from ophyd_async.core import (
    DetectorTrigger,
    StandardDetector,
    StandardFlyer,
    TriggerInfo,
    in_micros,
)
from ophyd_async.epics.motor import Motor
from ophyd_async.fastcs.panda import (
    HDFPanda,
    PcompInfo,
    SeqTable,
    SeqTableInfo,
    StaticSeqTableTriggerLogic,
)

# Plans utilized for system testing
# This module contains a collection of Bluesky plans designed for system testing.
# These plans are used to perform various types of scans and data collection routines
# using the Bluesky framework and ophyd_async devices. Each plan is decorated with
# metadata to attach data session information, ensuring that all collected data
# is properly annotated and organized.


def prepare_static_seq_table_flyer_and_detectors_with_same_trigger(
    flyer: StandardFlyer[SeqTableInfo],
    detectors: list[StandardDetector],
    number_of_frames: int,
    exposure: float,
    shutter_time: float,
    repeats: int = 1,
    period: float = 0.0,
    frame_timeout: float | None = None,
):
    """Prepare a hardware triggered flyable and one or more detectors.

    Prepare a hardware triggered flyable and one or more detectors with the
    same trigger. This method constructs TriggerInfo and a static sequence
    table from required parameters. The table is required to prepare the flyer,
    and the TriggerInfo is required to prepare the detector(s).

    This prepares all supplied detectors with the same trigger.

    """
    if not detectors:
        raise ValueError("No detectors provided. There must be at least one.")

    deadtime = max(det._controller.get_deadtime(exposure) for det in detectors)  # noqa: SLF001

    trigger_info = TriggerInfo(
        number_of_events=number_of_frames * repeats,
        trigger=DetectorTrigger.CONSTANT_GATE,
        deadtime=deadtime,
        livetime=exposure,
        exposure_timeout=frame_timeout,
    )
    trigger_time = number_of_frames * (exposure + deadtime)
    pre_delay = max(period - 2 * shutter_time - trigger_time, 0)

    table = (
        # Wait for pre-delay then open shutter
        SeqTable.row(
            time1=in_micros(pre_delay),
            time2=in_micros(shutter_time),
            outa2=True,
        )
        +
        # Keeping shutter open, do N triggers
        SeqTable.row(
            repeats=number_of_frames,
            time1=in_micros(exposure),
            outa1=True,
            outb1=True,
            time2=in_micros(deadtime),
            outa2=True,
        )
        +
        # Add the shutter close
        SeqTable.row(time2=in_micros(shutter_time))
    )

    table_info = SeqTableInfo(sequence_table=table, repeats=repeats)

    for det in detectors:
        yield from bps.prepare(det, trigger_info, wait=False, group="prep")
    yield from bps.prepare(flyer, table_info, wait=False, group="prep")
    yield from bps.wait(group="prep")


def fly_and_collect(
    stream_name: str,
    flyer: StandardFlyer[SeqTableInfo] | StandardFlyer[PcompInfo],
    detectors: list[StandardDetector],
):
    """Kickoff, complete and collect with a flyer and multiple detectors.

    This stub takes a flyer and one or more detectors that have been prepared. It
    declares a stream for the detectors, then kicks off the detectors and the flyer.
    The detectors are collected until the flyer and detectors have completed.

    """
    yield from bps.declare_stream(*detectors, name=stream_name, collect=True)
    yield from bps.kickoff(flyer, wait=True)
    for detector in detectors:
        yield from bps.kickoff(detector)

    # collect_while_completing
    group = short_uid(label="complete")

    yield from bps.complete(flyer, wait=False, group=group)
    for detector in detectors:
        yield from bps.complete(detector, wait=False, group=group)

    done = False
    while not done:
        try:
            yield from bps.wait(group=group, timeout=0.5)
        except TimeoutError:
            pass
        else:
            done = True
        yield from bps.collect(
            *detectors,
            return_payload=False,
            name=stream_name,
        )
    yield from bps.wait(group=group)


@attach_data_session_metadata_decorator()
def fly_and_collect_plan(panda: HDFPanda, diff: StandardDetector) -> MsgGenerator:
    trigger_logic = StaticSeqTableTriggerLogic(panda.seq[1])
    flyer = StandardFlyer(
        trigger_logic,
        name="flyer",
    )

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
