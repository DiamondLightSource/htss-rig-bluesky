def test_import_bluesky():
    import bluesky.plan_stubs as bps  # noqa: F401
    import bluesky.plans as bp  # noqa: F401
    from bluesky import RunEngine  # noqa: F401
    from bluesky.callbacks.best_effort import BestEffortCallback  # noqa: F401


def test_import_dodal():
    from dodal.utils import make_all_devices  # noqa: F401


def test_import_local():
    import htss.devices as devices  # noqa: F401
    from htss.data_access import get_client, print_docs  # noqa: F401
    from htss.names import BEAMLINE  # noqa: F401
    from htss.plans.calibration import scan_center, scan_exposure  # noqa: F401
    from htss.plans.detector import Roi, ensure_detector_ready, set_roi  # noqa: F401
    from htss.plans.exercise import (  # noqa: F401
        ensure_detector_ready,
        exercise_beamline,
        exercise_detector,
        exercise_motors,
        exercise_scan,
    )
    from htss.plans.tomography import tomography_scan  # noqa: F401
    from htss.plotting.centering import plot_sum_and_center_of_mass  # noqa: F401
    from htss.plotting.cropping import croppable_plot  # noqa: F401
    from htss.plotting.images import plot_images_vs_axis  # noqa: F401
    from htss.processing.centering import find_center_of_mass, find_sum  # noqa: F401
    from htss.processing.tomography import normalize_tomography_data  # noqa: F401


def test_import_matplotlib():
    import matplotlib  # noqa: F401
    import matplotlib.pyplot as plt  # noqa: F401
