from collections.abc import Generator
from typing import Any

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.protocols import Movable, Readable
from bluesky.utils import MsgGenerator
from ophyd_async.fastcs.panda import HDFPanda
from scanspec.core import Axis
from scanspec.specs import Spec

from htss_rig_bluesky.models import (
    THETA,
    Darks,
    Flats,
    Projections,
    TomographySpec,
    X,
)
from htss_rig_bluesky.plans.backlight import set_backlight_intensity


def default_tomography_scan(
    detectors: list[Readable],
    panda: HDFPanda,
    x: Movable,
    theta: Movable,
) -> MsgGenerator:
    spec = TomographySpec.default()
    yield from tomography_step_scan(
        detectors,
        panda,
        x,
        theta,
        spec,
        {},
    )


def tomography_step_scan(
    detectors: list[Readable],
    panda: HDFPanda, 
    x: Movable,
    theta: Movable,
    tomo_spec: TomographySpec,
    metadata: dict[str, Any] | None = None,
) -> MsgGenerator:
    """
    Perform a tomography scan.

    Take a series of darks, flats and projects, and emit events for them in separate
    streams named "darks" and "flats". Optionally take the projections over a range
    of x values for samples that are too big to fit in the beam.

    Args:
        detectors: Detectors that should image darks, flats and projections
        beam: A movable device that can be used to turn the beam on and off
        x: A movable device that can be used to move the sample linearly
        theta: A movable device that can be used to rotate the sample
        tomo_spec: Specification of the scan trajectory
        metadata (Optional[Dict[str, Any]], optional): Any additional key/value metadata
            for the scan. Defaults to None.

    Yields:
        Plan
    """

    metadata = {
        "plan_name": tomography_step_scan.__name__,
        "tomo_spec": tomo_spec.model_dump(),
    } | (metadata or {})

    # If a motor can be read, we record its position
    readable_motors = [motor for motor in {x, theta} if isinstance(motor, Readable)]
    all_detectors = detectors + readable_motors
    axis_lookup = {
        X: x,
        THETA: theta,
    }

    def do_move(point: dict[Axis, float]) -> MsgGenerator:
        for axis, pos in point.items():
            yield from bps.abs_set(
                axis_lookup[axis],
                pos,
                wait=False,
                group="move_axes",
            )
        yield from bps.wait(group="move_axes")

    def do_count(num: int, stream_name: str) -> MsgGenerator:
        for _ in range(num):
            yield from collect_for_stream(all_detectors, stream_name)

    def do_scan(spec: Spec[str], stream_name: str) -> MsgGenerator:
        for point in spec.midpoints():
            yield from do_move(point)
            yield from do_count(1, stream_name)

    from dodal.plan_stubs.data_session import attach_data_session_metadata_decorator

    @attach_data_session_metadata_decorator()
    @bpp.run_decorator(md=metadata)
    @bpp.stage_decorator(all_detectors)
    def do_tomography() -> MsgGenerator:
        for stream_name in tomo_spec.all_stream_names():
            yield from bps.declare_stream(
                *all_detectors,
                name=stream_name,
            )
        for operation in tomo_spec.sample_operations:
            yield from bps.checkpoint()
            match operation:
                case Darks(
                    num=num,
                    stream_name=stream_name,
                ):
                    yield from set_backlight_intensity(panda, 0.0)
                    yield from do_count(num, stream_name)
                case Flats(
                    num=num,
                    out_of_beam=out_of_beam,
                    stream_name=stream_name,
                ):
                    yield from set_backlight_intensity(panda, 1.0)
                    original_x_position = yield from bps.rd(x)
                    yield from bps.abs_set(x, out_of_beam)
                    yield from do_count(num, stream_name)
                    yield from bps.abs_set(x, original_x_position)
                case Projections(
                    scanspec=scanspec,
                    stream_name=stream_name,
                ):
                    yield from set_backlight_intensity(panda, 1.0)
                    yield from do_scan(scanspec, stream_name)
                case _:
                    raise KeyError(f"Unknown operation type: {operation}")

    yield from do_tomography()


def collect_for_stream(detectors: list[Readable], stream_name: str) -> Generator:
    yield from bps.trigger_and_read(detectors, name=stream_name)
