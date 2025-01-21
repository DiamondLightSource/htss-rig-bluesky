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
    BEAM,
    THETA,
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
            if axis == BEAM:
                yield from set_backlight_intensity(
                    panda,
                    pos,
                    wait=False,
                    group="move_axes",
                )
            else:
                yield from bps.abs_set(
                    axis_lookup[axis],
                    pos,
                    wait=False,
                    group="move_axes",
                )
        yield from bps.wait(group="move_axes")

    def do_scan(spec: Spec[str], stream_name: str) -> MsgGenerator:
        for point in spec.midpoints():
            yield from do_move(point)
            yield from collect_for_stream(all_detectors, stream_name)

    from dodal.plan_stubs.data_session import attach_data_session_metadata_decorator

    @attach_data_session_metadata_decorator()
    @bpp.run_decorator(md=metadata)
    @bpp.stage_decorator(detectors)
    def do_tomography() -> MsgGenerator:
        used_stream_names = set()
        for operation in tomo_spec.sample_operations:
            # Declare a new data stream if needed
            stream_name = operation.stream_name
            if stream_name not in used_stream_names:
                yield from bps.checkpoint()
                yield from bps.declare_stream(
                    *all_detectors,
                    name=stream_name,
                )
            used_stream_names.add(stream_name)

            # Collect data for operation
            yield from bps.checkpoint()
            as_scanspec = operation.as_scanspec()
            yield from do_scan(as_scanspec, stream_name)

    yield from do_tomography()


def collect_for_stream(detectors: list[Readable], stream_name: str) -> Generator:
    yield from bps.trigger_and_read(detectors, name=stream_name)
