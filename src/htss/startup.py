import bluesky.plan_stubs as bps  # noqa: F401
import bluesky.plans as bp  # noqa: F401
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

globals().update(make_all_devices(devices))

bec = BestEffortCallback()
bec.disable_plots()

RE = RunEngine()
RE.subscribe(bec)

startup_message = f"Startup completed, Bluesky in control of {devices.BEAMLINE}"
bar = "=" * len(startup_message)
print(bar)
print(startup_message)
print(bar)
