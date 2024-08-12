def test_import_bluesky():
    import bluesky.plan_stubs as bps  # noqa: F401
    import bluesky.plans as bp  # noqa: F401
    from bluesky import RunEngine  # noqa: F401
    from bluesky.callbacks.best_effort import BestEffortCallback  # noqa: F401


def test_import_dodal():
    from dodal.utils import make_all_devices  # noqa: F401


def test_import_local():
    import htss_rig_bluesky.devices as devices  # noqa: F401
    from htss_rig_bluesky.data_access import get_client, print_docs  # noqa: F401
    from htss_rig_bluesky.names import BEAMLINE  # noqa: F401
    from htss_rig_bluesky.plans.calibration import (  # noqa: F401
        scan_center,
        scan_exposure,
    )
    from htss_rig_bluesky.plans.detector import (  # noqa: F401
        Roi,
        ensure_detector_ready,
        set_roi,
    )
    from htss_rig_bluesky.plans.exercise import (  # noqa: F401
        ensure_detector_ready,
        exercise_beamline,
        exercise_detector,
        exercise_motors,
        exercise_scan,
    )
    from htss_rig_bluesky.plans.tomography import tomography_scan  # noqa: F401
    from htss_rig_bluesky.plotting.centering import (
        plot_sum_and_center_of_mass,  # noqa: F401
    )
    from htss_rig_bluesky.plotting.cropping import croppable_plot  # noqa: F401
    from htss_rig_bluesky.plotting.images import plot_images_vs_axis  # noqa: F401
    from htss_rig_bluesky.processing.centering import (  # noqa: F401
        find_center_of_mass,
        find_sum,
    )
    from htss_rig_bluesky.processing.tomography import (
        normalize_tomography_data,  # noqa: F401
    )


def test_import_matplotlib():
    import matplotlib  # noqa: F401
    import matplotlib.pyplot as plt  # noqa: F401
