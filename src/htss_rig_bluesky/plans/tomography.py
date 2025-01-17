from collections.abc import Generator
from typing import Any

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.protocols import Movable, Readable
from bluesky.utils import MsgGenerator
from dodal.plan_stubs.data_session import attach_data_session_metadata_decorator
from scanspec.core import Axis
from scanspec.specs import Spec

from htss_rig_bluesky.models import (
    BEAM,
    THETA,
    Darks,
    Flats,
    Projections,
    TomographySpec,
    X,
)


def tomography_step_scan(
    detectors: list[Readable],
    beam: Movable,
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

    darks = "darks"
    flats = "flats"
    projections = "projections"

    metadata = {
        "plan_name": tomography_step_scan.__name__,
    } | (metadata or {})

    all_detectors = detectors + [beam, x, theta]
    axis_lookup = {
        X: x,
        THETA: theta,
        BEAM: beam,
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

    def do_scan(spec: Spec[str], stream_name: str) -> MsgGenerator:
        for point in spec.midpoints():
            yield from do_move(point)
            yield from collect_for_stream(all_detectors, stream_name)

    @attach_data_session_metadata_decorator()
    @bpp.run_decorator(md=metadata)
    @bpp.stage_decorator(detectors)
    def do_tomography() -> MsgGenerator:
        for stream_name in (darks, flats, projections):
            yield from bps.declare_stream(*all_detectors, name=stream_name)

        for stage in iter(tomo_spec):
            as_scanspec = stage.operation.to_spec()
            stream_name = {Darks: darks, Flats: flats, Projections: projections}[
                type(stage.operation)
            ]
            yield from do_scan(as_scanspec, stream_name)

    yield from do_tomography()


def collect_for_stream(detectors: list[Readable], stream_name: str) -> Generator:
    yield from bps.trigger_and_read(detectors, name=stream_name)
