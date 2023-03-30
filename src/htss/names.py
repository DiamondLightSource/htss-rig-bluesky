import os
from typing import Mapping

BEAMLINE = os.environ.get("BEAMLINE", "")


def pv_prefix() -> str:
    return _lookup({"p46": "BL46P", "p47": "BL47P", "p48": "BL46P", "p49": "BL49P"})


def server_name() -> str:
    return _lookup(
        {
            "p46": "bl46p-ea-serv-01.diamond.ac.uk",
            "p47": "bl47p-ea-serv-01.diamond.ac.uk",
            "p48": "bl48p-ea-serv-01.diamond.ac.uk",
            "p49": "bl49p-ea-serv-01.diamond.ac.uk",
        }
    )


def _lookup(mapping: Mapping[str, str]) -> str:
    beamline = BEAMLINE.lower()
    if beamline not in mapping.keys():
        raise KeyError(f"Please set $BEAMLINE to one of {list(mapping.keys())}")
    return mapping[beamline]
