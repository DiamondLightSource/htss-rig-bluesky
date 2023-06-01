from typing import Any, Dict, Generator, Optional

import bluesky.plan_stubs as bps
import bluesky.plans as bp
from bluesky.protocols import Movable, Readable
from ophyd import pv_positioner

from htss.devices import AdAravisDetector, SampleStage

import numpy as np
import bluesky.preprocessors as bpp


def tomography_scan(
    detectors: list[Readable],
    x: Movable,
    theta: Movable,
    min_theta: float = 0.0,
    max_theta: float = 180.0,
    num_projections: int = 90,
    num_darks: Optional[int] = None,
    num_flats: Optional[int] = None,
    beam_centre: Optional[float] = None,
    out_of_beam: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Generator:
    # If no beam centre is supplied, assume x is already there
    beam_centre = beam_centre or (yield from bps.rd(x))
    out_of_beam = out_of_beam or beam_centre + 5.0
    num_aux_images = int(max(num_projections / 10, 6))
    num_darks = num_darks or num_aux_images
    num_flats = num_flats or num_aux_images

    for motor in (x, theta):
        if isinstance(motor, Readable):
            detectors.append(motor)

    metadata = {
        "detectors": [det.name for det in detectors],
        "min_theta": min_theta,
        "max_theta": max_theta,
        "num_projections": num_projections,
        "num_darks": num_darks,
        "num_flats": num_flats,
        "beam_centre": beam_centre,
        "out_of_beam": out_of_beam,
        **(metadata or {}),
    }

    yield from bps.mv(
        x,
        beam_centre,
        theta,
        min_theta,
    )

    flats = collect_flats(detectors, x, num_flats, out_of_beam)
    darks = collect_darks(detectors, num_darks)
    projections = collect_projections(
        detectors, theta, min_theta, max_theta, num_projections
    )

    @bpp.run_decorator(md=metadata)
    @bpp.stage_decorator(detectors)
    def do_tomography() -> Generator:
        yield from flats
        yield from darks
        yield from projections

    return (yield from do_tomography())


def collect_projections(
    detectors: list[Readable],
    theta: Movable,
    start: float,
    stop: float,
    num: int,
) -> Generator:
    for step in np.linspace(start, stop, num):
        yield from bps.one_1d_step(detectors, theta, step)


def collect_darks(
    detectors: list[Readable],
    num_darks: int,
) -> Generator:
    yield from bps.repeat(
        partial(collect_for_stream, detectors, "darks"), num=num_darks
    )


from functools import partial


def collect_flats(
    detectors: list[Readable],
    x: Movable,
    num_flats: int,
    out_of_the_way: float,
) -> Generator:
    previous_position = yield from bps.rd(x)
    yield from bps.mv(x, out_of_the_way)
    yield from bps.repeat(
        partial(collect_for_stream, detectors, "flats"), num=num_flats
    )
    yield from bps.mv(x, previous_position)


def collect_for_stream(detectors: list[Readable], stream: str) -> Generator:
    yield from bps.trigger_and_read(detectors, name=stream)
