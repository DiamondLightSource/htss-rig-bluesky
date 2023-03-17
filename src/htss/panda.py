from typing import Any, List

from ophyd import Signal
from pandablocks.blocking import BlockingClient
from pandablocks.commands import Get, Put


class PandablocksSignal(Signal):
    _network_addr: str
    _block_addr: str

    def put(self, value: Any, *, timeout: float = ..., **kwargs):
        with BlockingClient(self._network_addr) as client:
            # Commands sent to Control port
            client.send(self._put_cmd(value))

    def get(self, **kwargs):
        with BlockingClient(self._network_addr) as client:
            # Commands sent to Control port
            value = client.send(self._get_cmd())
        return value

    def _get_cmd(self) -> Get:
        return Get(f"{self._block_addr}?")

    def _put_cmd(self, value: Any) -> Put:
        return Put(self._block_addr, value)
