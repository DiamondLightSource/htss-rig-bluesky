from collections import defaultdict
from typing import Any, Dict, Generator, Optional

import bluesky.plan_stubs as bps
import bluesky.plans as bp
from bluesky.protocols import Movable, Readable
from ophyd import pv_positioner

from htss.devices import AdAravisDetector, SampleStage

import numpy as np
import bluesky.preprocessors as bpp

from typing import Union

from scanspec.specs import Line


def tomography_scan(
    detectors: list[Readable],
    x: Movable,
    theta: Movable,
    min_theta: float = 0.0,
    max_theta: float = 180.0,
    num_projections: int = 90,
    num_darks: Optional[int] = None,
    num_flats: Optional[int] = None,
    x_start: Optional[float] = None,
    x_stop: Optional[float] = None,
    x_steps: Optional[int] = None,
    out_of_beam: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Generator:
    # If no beam centre is supplied, assume x is already there
    if x_start is None:
        x_start = yield from bps.rd(x)
    if x_steps is None:
        x_steps = 1
    if x_stop is None:
        x_stop = x_start

    out_of_beam = out_of_beam or 0.0
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
        "x_start": x_start,
        "x_stop": x_stop,
        "x_steps": x_steps,
        "out_of_beam": out_of_beam,
        **(metadata or {}),
    }

    flats = collect_flats(detectors, x, num_flats, out_of_beam)
    darks = collect_darks(detectors, num_darks)
    projections = collect_projections(
        detectors,
        theta,
        min_theta,
        max_theta,
        num_projections,
        x,
        x_start,
        x_stop,
        x_steps,
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
    theta_start: float,
    theta_stop: float,
    theta_num: int,
    x: Movable,
    x_start: float,
    x_stop: float,
    x_num: int,
) -> Generator:
    for x_pos in np.linspace(x_start, x_stop, x_num):
        for theta_pos in np.linspace(theta_start, theta_stop, theta_num):
            yield from bps.one_nd_step(
                detectors,
                {x: x_pos, theta: theta_pos},
                defaultdict(lambda: None),
            )


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
