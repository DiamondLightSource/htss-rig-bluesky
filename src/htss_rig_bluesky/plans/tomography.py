from collections import defaultdict
from collections.abc import Generator
from functools import partial
from typing import Any

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
import numpy as np
from bluesky.protocols import Movable, Readable
from pydantic import BaseModel
from typing import Literal
from scanspec.specs import Spec, Line, Static
from bluesky.utils import MsgGenerator
from dodal.plans import spec_scan
THETA = "theta"
X = "x"
BEAM = "beam"


class AxisTrajectory(BaseModel):
    start: float
    stop: float
    num: int

class TomoTrajectory(BaseModel):
    outer_trajectory: AxisTrajectory | None = None
    trajectory: AxisTrajectory

    def to_spec(self) -> Spec:
        inner = Line(THETA, self.trajectory.start, self.trajectory.stop, self.trajectory.num)
        if self.outer_trajectory is not None:
            outer = Line(X, self.outer_trajectory.start, self.outer_trajectory.stop, self.outer_trajectory.num)
            return outer * inner
        else:
            return inner

class Darks(BaseModel):
    num: int

    def to_spec(self) -> Spec:
        return Static(BEAM, 0).repeat(self.num)

class Flats(BaseModel):
    num: int
    out_of_beam: float | Literal["high", "low"] = "low"

    def to_spec(self) -> Spec:
        return (Static(BEAM, 1) & Static(X, self.out_of_beam)).repeat(self.num)


class Projections(BaseModel):
    trajectory: TomoTrajectory

    def to_spec(self) -> Spec:
        return self.trajectory.to_spec()


class TomographySpec(BaseModel):
    operation: Darks | Flats | Projections
    next_stage: "TomographySpec" | None = None

    @classmethod
    def default(cls, scale: int = 1) -> "TomographySpec":
        dark_stage = Darks(num=1 * scale)
        flat_stage = Flats(num=1 * scale)
        projection_stage = Projections(trajectory=TomoTrajectory(trajectory=AxisTrajectory(start=-180.0, stop=180, num=5 * scale)))
        return cls(
            operation=dark_stage
            next_stage=cls(
                operation=flat_stage,
                next_stage=cls(
                    operation=projection_stage,
                )
            )
        )

    def __iter__(self):
        yield self
        if self.next_stage is not None:
            yield from iter(self.next_stage)


def tomography_step_scan(
    detectors: list[Readable],
    beam: Movable,
    x: Movable,
    theta: Movable,
    tomo_spec: TomographySpec,
    metadata: dict[str, Any] | None = None,
) -> MsgGenerator:
    yield from bps.dec

    for stage in iter(tomo_spec):
        as_scanspec = stage.to_spec()
        if isinstance(stage.operation, Darks):
            ...


def tomography_scan(
    detectors: list[Readable],
    beam: Movable,
    x: Movable,
    theta: Movable,
    min_theta: float = 0.0,
    max_theta: float = 180.0,
    num_projections: int = 90,
    num_darks: int | None = None,
    num_flats: int | None = None,
    x_start: float | None = None,
    x_stop: float | None = None,
    x_steps: int | None = None,
    out_of_beam: float = 0.0,
    metadata: dict[str, Any] | None = None,
) -> Generator:
    """
    Perform a tomography scan.

    Take a series of darks and flats, and emit events for them in separate streams
    named "darks" and "flats". Then take a series of projections in the "primary"
    stream. Optionally take the projections over a range of x values for samples
    that are too big to fit in the beam.

    Args:
        detectors: Detectors that should image darks, flats and projections
        beam: A movable device that can be used to turn the beam on and off
        x: A movable device that can be used to move the sample linearly
        theta: A movable device that can be used to rotate the sample
        min_theta: The lowest theta value when taking projections. Defaults to 0.0.
        max_theta: The highest theta value when taking projections. Defaults to 180.0.
        num_projections: Number of projections to take. Defaults to 90.
        num_darks: Number of darks to take. Defaults to 6 or 10% of num_projections,
            whichever is higher.
        num_flats: Number of flats to take. Defaults to 6 or 10% of num_projections,
            whichever is higher.
        x_start: If moving x, where to start, if not moving x, where to center the
            sample. Defaults to the current x position of the sample.
        x_stop: If moving x, where to stop. Defaults to None.
        x_steps: If moving x, how many steps. Defaults to None.
        out_of_beam: An x position that has the sample out of the beam, for
            taking flats. Defaults to 0.0.
        metadata (Optional[Dict[str, Any]], optional): Any additional key/value metadata
            for the scan. Defaults to None.

    Yields:
        Plan
    """

    # If no beam centre is supplied, assume x is already there
    if x_start is None:
        x_start = yield from bps.rd(x)
    if x_steps is None:
        x_steps = 1
    if x_stop is None:
        x_stop = x_start

    num_aux_images = int(max(num_projections / 10, 6))
    num_darks = num_darks or num_aux_images
    num_flats = num_flats or num_aux_images

    for movable in (x, theta, beam):
        if isinstance(movable, Readable):
            detectors.append(movable)

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

    flats = collect_flats(
        detectors,
        beam,
        x,
        num_flats,
        out_of_beam,
    )
    darks = collect_darks(
        detectors,
        beam,
        num_darks,
    )
    projections = collect_projections(
        detectors,
        beam,
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
    beam: Movable,
    theta: Movable,
    theta_start: float,
    theta_stop: float,
    theta_num: int,
    x: Movable,
    x_start: float,
    x_stop: float,
    x_num: int,
) -> Generator:
    yield from bps.abs_set(beam, True)
    for x_pos in np.linspace(x_start, x_stop, x_num):
        for theta_pos in np.linspace(theta_start, theta_stop, theta_num):
            yield from bps.one_nd_step(
                detectors,
                {x: x_pos, theta: theta_pos},
                defaultdict(lambda: None),
            )


def collect_darks(
    detectors: list[Readable],
    beam: Movable,
    num_darks: int,
) -> Generator:
    yield from bps.abs_set(beam, False)
    yield from bps.repeat(
        partial(collect_for_stream, detectors, "darks"), num=num_darks
    )


def collect_flats(
    detectors: list[Readable],
    beam: Movable,
    x: Movable,
    num_flats: int,
    out_of_the_way: float,
) -> Generator:
    yield from bps.abs_set(beam, True)
    previous_position = yield from bps.rd(x)
    yield from bps.mv(x, out_of_the_way)
    yield from bps.repeat(
        partial(collect_for_stream, detectors, "flats"), num=num_flats
    )
    yield from bps.mv(x, previous_position)


def collect_for_stream(detectors: list[Readable], stream: str) -> Generator:
    yield from bps.trigger_and_read(detectors, name=stream)
