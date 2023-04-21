from typing import Generator, Optional, Any

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
import numpy as np
from htss.devices import AdAravisDetector, SampleStage


def single_run_tomo(
        det: AdAravisDetector,
        sample: SampleStage,
        beam_centre: float = 0.0,
        num_flats: int = 5,
        rot_start: float = 0,
        rot_stop: float = 0,
        rot_steps: int = 18,
        metadata: Optional[dict[str, Any]] = None,
) -> Generator:
    # Prepare detector
    yield from bps.mv(
        det.cam.num_exposures,
        1,
        det.cam.acquire_period,
        0.1,
        det.cam.acquire_time,
        0.15,
    )

    # We add metadata about the plan we ran and how to reconstruct some of its data to the Run
    _md = {'detectors': [det.name],
           'motors': [sample.x.name],
           'num_points': rot_steps,
           'num_intervals': rot_steps - 1,
           'plan_args': {'det': repr(det),
                         'sample': repr(sample),
                         'beam_centre': beam_centre,
                         'num_flats': num_flats,
                         'rot_start': rot_start,
                         'rot_stop': rot_stop,
                         'rot_steps': rot_steps},
           'plan_name': 'single_run_tomo',
           **(metadata or {})
           }

    # We use the run_decorator to conveniently parcel all the following data
    @bpp.run_decorator(_md=_md)
    # We wrap our plan logic in an inner method to allow us to stage and unstage our devices exactly once
    @bpp.stage_decorator(det, sample)
    def do_tomography():

        def collect_flats():
            # We read our flats into the same Run but in a different Stream
            yield from bps.trigger_and_read(det, name="flats")

        # Move sample out of the way
        yield from bps.mv(sample.x, -24.9)
        # Take 5 flats
        yield from bps.repeat(collect_flats, num=num_flats)
        # Move sample into beam
        yield from bps.mv(sample.x, beam_centre)
        # Take projections
        # Numpy is already dependency of Bluesky, this is how they do _scan_1d
        for step in np.linspace(rot_start, rot_stop, rot_steps):
            yield from bps.one_1d_step(det, sample.x, step)

    return (yield from do_tomography())
