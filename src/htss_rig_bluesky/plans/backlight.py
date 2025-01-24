import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from ophyd_async.fastcs.panda import HDFPanda


def set_backlight_intensity(
    panda: HDFPanda,
    intensity: float,
    wait: bool = True,
    group: str | None = None,
) -> MsgGenerator[None]:
    if 0.0 <= intensity <= 1.0:
        duty_cycle = int(round(intensity * 100.0))
        if duty_cycle == 0:
            port = "ZERO"
        elif duty_cycle == 100:
            port = "ONE"
        else:
            port = yield from create_pwm(panda, duty_cycle, wait, group)

        yield from set_backlight_control_port(panda, port, wait, group)
    else:
        raise ValueError(f"Given intensity {intensity} should be between 0.0 and 1.0")


def set_backlight_control_port(
    panda: HDFPanda,
    port: str,
    wait: bool = True,
    group: str | None = None,
) -> MsgGenerator[None]:
    ttl_out_2 = panda.ttlout[2]
    yield from bps.abs_set(
        ttl_out_2.val,
        port,
        wait=wait,
        group=group,
    )


def create_pwm(
    panda: HDFPanda,
    duty_cycle: int,
    wait: bool = True,
    group: str | None = None,
) -> MsgGenerator[str]:
    return NotImplemented
