import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from ophyd_async.fastcs.panda import HDFPanda, TimeUnits


def set_backlight_intensity(
    panda: HDFPanda,
    intensity: float,
    wait: bool = True,
    group: str | None = None,
) -> MsgGenerator[None]:
    if 0.0 <= intensity <= 1.0:
        group = group or set_backlight_intensity.__name__
        duty_cycle = int(round(intensity * 100))

        if duty_cycle == 0:
            port = "ZERO"
        elif duty_cycle == 100:
            port = "ONE"
        else:
            port = yield from create_pwm(panda, intensity, wait=False, group=group)

        yield from set_backlight_control_port(panda, port, wait=False, group=group)

        if wait:
            yield from bps.wait(group=group)
    else:
        raise ValueError(f"Given intensity {intensity} should be between 0.0 and 1.0")


def create_pwm(
    panda: HDFPanda,
    duty_cycle: float,
    period: float = 100.0,
    wait: bool = True,
    group: str | None = None,
) -> MsgGenerator[str]:
    live_time = period * duty_cycle
    dead_time = period - live_time

    clock = panda.clock[2]
    pulse = panda.pulse[2]

    group = group or create_pwm.__name__

    for signal, value in {
        # Set units first
        clock.period_units: TimeUnits.US,
        pulse.delay_units: TimeUnits.US,
        pulse.width_units: TimeUnits.US,
        # Then set all other values
        clock.enable: "ONE",
        clock.enable_delay: 0.0,
        clock.period: period,
        pulse.enable: "ONE",
        pulse.trig: "CLOCK2.OUT",
        pulse.delay: dead_time,
        pulse.width: live_time,
        pulse.trig_edge: "Rising",
    }.items():
        yield from bps.abs_set(signal, value, wait=False, group=group)

    if wait:
        yield from bps.wait(group)

    return "PULSE2.OUT"


def set_backlight_control_port(
    panda: HDFPanda,
    port: str,
    wait: bool = True,
    group: str | None = None,
) -> MsgGenerator[None]:
    output_port = panda.ttlout[2]
    yield from bps.abs_set(
        output_port.val,
        port,
        wait=wait,
        group=group,
    )
