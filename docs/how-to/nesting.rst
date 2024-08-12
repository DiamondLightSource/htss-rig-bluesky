Nest Plans
==========

.. note::

    Requires a `Development Environment <./dev-environment>`.

A common use case is to pass plans to plans and nest dynamic operations,
for example:

.. code:: python

    from typing import Callable, Generator

    import bluesky.plan_stubs as bps
    import bluesky.plans as bp

    from htss.devices import AdAravisDetector, SampleStage
    from htss.plans.detector import Roi, set_roi


    def basic_tomo(
        det: AdAravisDetector,
        sample: SampleStage,
        prepare_detector: Callable[[AdAravisDetector], Generator],
        beam_centre: float = 0.0,
    ) -> Generator:
        # Prepare detector
        yield from prepare_detector(det)

        # Move sample out of the way and take 5 flats
        yield from bps.mv(sample.x, -24.9)
        yield from bp.count([det], num=5)

        # Move sample into beam and take projections
        yield from bps.mv(sample.x, beam_centre)
        yield from bp.scan([det], sample.theta, 0.0, 180.0, 18)


    def basic_detector_setup(det: AdAravisDetector) -> Generator:
        yield from bps.mv(
            det.cam.num_exposures,
            1,
            det.cam.acquire_period,
            0.1,
            det.cam.acquire_time,
            0.15,
        )


    def narrow_field_setup(det: AdAravisDetector) -> Generator:
        yield from set_roi(det, Roi(0, 600, size_y=20))
        yield from bps.mv(
            det.cam.num_exposures,
            10,
            det.cam.acquire_period,
            0.1,
            det.cam.acquire_time,
            0.15,
        )


You can then see that the detector is setup differently when running the following 
two commands:

.. code:: IPython

    In [1]: RE(basic_tomo(det, sample_stage, basic_detector_setup))

    In [2]: RE(basic_tomo(det, sample_stage, narrow_field_setup))


.. _Bluesky: https://blueskyproject.io/bluesky/
