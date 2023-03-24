import bluesky.plan_stubs as bps  # noqa: F401
import bluesky.plans as bp  # noqa: F401
from bluesky import RunEngine
from dodal.utils import make_all_devices

import htss.devices as devices
from htss.plans.excercise import (  # noqa: F401
    excercise_beamline,
    excercise_detector,
    excercise_motors,
    exercise_scan,
)

globals().update(make_all_devices(devices))


RE = RunEngine()
