import os

import bluesky.plan_stubs as bps  # noqa: F401
import bluesky.plans as bp  # noqa: F401
import matplotlib
import matplotlib.pyplot as plt  # noqa: F401
from bluesky import RunEngine
from bluesky.callbacks.best_effort import BestEffortCallback
from dodal.utils import make_all_devices

import htss.devices as devices
from htss.plans.excercise import (  # noqa: F401
    excercise_beamline,
    excercise_detector,
    excercise_motors,
    excercise_scan,
)

from .data_access import get_client
from .names import BEAMLINE

matplotlib.use("QtAgg")

globals().update(make_all_devices(devices))

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
