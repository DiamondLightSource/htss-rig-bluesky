from typing import Optional
from softioc import softioc, builder, asyncio_dispatcher
from softioc.alarm import MINOR_ALARM, STATE_ALARM, NO_ALARM
import asyncio

# from htss.names import pv_prefix

from pandablocks.asyncio import AsyncioClient
from pandablocks.commands import Put, Get


def create_ioc() -> None:
    # Create an asyncio dispatcher, the event loop is now running
    dispatcher = asyncio_dispatcher.AsyncioDispatcher()

    # Set the record prefix
    prefix = "BL47P"
    builder.SetDeviceName(f"{prefix}-EA-BEAM-01")

    # Create some records
    readback = builder.boolIn(
        "State_RBV",
        ZNAM="Off",
        ONAM="On",
    )

    async def update_panda(demand: bool) -> None:
        await set_light_state(demand)

    demand = builder.boolOut(
        "State",
        ZNAM="Off",
        ONAM="On",
        always_update=True,
        on_update=update_panda,
    )

    # Boilerplate get the IOC started
    builder.LoadDatabase()
    softioc.iocInit(dispatcher)

    # Start processes required to be run after iocInit
    async def update_rbv() -> None:
        while True:
            # Read and update the state of the light from the
            # panda at 2Hz
            current_state = await get_light_state()
            readback.set(current_state or False)
            if current_state is None:
                # Someone could configure the panda to
                # conditionally turn the light on.
                # This simple IOC does not support this so
                # should report an error if this occurs.
                readback.set_alarm(MINOR_ALARM, STATE_ALARM)
            else:
                readback.set_alarm(NO_ALARM, STATE_ALARM)
            await asyncio.sleep(0.5)

    dispatcher(update_rbv)

    # Finally leave the IOC running with an interactive shell.
    softioc.interactive_ioc(locals())


HTSS_PANDA_IP = "192.168.250.18"


async def set_light_state(demand: bool, addr: str = HTSS_PANDA_IP) -> None:
    panda_demand = "ONE" if demand else "ZERO"
    async with AsyncioClient(addr) as panda:
        await panda.send(Put("TTLOUT2.VAL", panda_demand))


async def get_light_state(addr: str = HTSS_PANDA_IP) -> Optional[bool]:
    async with AsyncioClient(addr) as panda:
        readback = await panda.send(Get("TTLOUT2.VAL"))

    return {"ONE": True, "ZERO": False}.get(readback)


if __name__ == "__main__":
    create_ioc()
