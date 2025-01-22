import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from ophyd_async.fastcs.panda import HDFPanda


def set_backlight_intensity(
    panda: HDFPanda,
    intensity: float,
    wait: bool = True,
    group: str | None = None,
) -> MsgGenerator:
    if not 0.0 <= intensity <= 1.0:
        raise ValueError(f"Given intensity {intensity} should be between 0.0 and 1.0")

    put_value = {1: "ONE", 0: "ZERO"}[int(round(intensity))]
    ttl_out_2 = panda.ttlout[2]

    yield from bps.abs_set(
        ttl_out_2.val,
        put_value,
        wait=wait,
        group=group,
    )
