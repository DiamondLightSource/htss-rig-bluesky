import os
from pprint import pprint  # noqa: F401

import bluesky.plan_stubs as bps  # noqa: F401
import bluesky.plans as bp  # noqa: F401
import matplotlib
import matplotlib.pyplot as plt  # noqa: F401
import numpy as np  # noqa: F401
from bluesky import RunEngine
from bluesky.callbacks.best_effort import BestEffortCallback
from dodal.utils import make_all_devices

import htss_rig_bluesky.devices as devices
from htss_rig_bluesky.plans.calibration import scan_center, scan_exposure  # noqa: F401
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

from .data_access import get_client, print_docs  # noqa: F401
from .names import BEAMLINE

# Required to suppress harmless warnings resulting from
# the networking setup
devices.suppress_epics_warnings()

matplotlib.use("QtAgg")

successful_devices, errors = make_all_devices(devices)
if len(errors) > 0:
    print(f"The following devices failed to connect{errors}")

globals().update(successful_devices)

bec = BestEffortCallback()

RE = RunEngine()
RE.subscribe(bec)

if os.environ.get("MINIMAL", False):
    bec.disable_plots()
else:
    tiled = get_client()
    tiled.login(username="htss")
    RE.subscribe(tiled.post_document)

startup_message = f"Startup completed, Bluesky in control of {BEAMLINE}"
bar = "=" * len(startup_message)
print(bar)
print(startup_message)
print(bar)
