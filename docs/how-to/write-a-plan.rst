Write a Plan
============

.. note::

    Requires a `Development Environment <./dev-environment>`.

You can write custom plans with their own logic and compose them together with existing plans.
See Bluesky_ documentation for more.

.. code:: python

    from typing import Generator

    import bluesky.plan_stubs as bps
    import bluesky.plans as bp

    from htss.devices import AdAravisDetector, SampleStage


    def basic_tomo(
        det: AdAravisDetector, sample: SampleStage, beam_centre: float = 0.0
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

        # Move sample out of the way and take 5 flats
        yield from bps.mv(sample.x, -24.9)
        yield from bp.count([det], num=5)

        # Move sample into beam and take projections
        yield from bps.mv(sample.x, beam_centre)
        yield from bp.scan([det], sample.theta, 0.0, 180.0, 18)


Run with:

.. code:: IPython

    [1]: RE(basic_tomo(det, sample_stage))


.. _Bluesky: https://blueskyproject.io/bluesky/
