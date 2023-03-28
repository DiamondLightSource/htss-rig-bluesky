htss-rig-bluesky
===========================

|code_ci| |docs_ci| |coverage| |pypi_version| |license|

Collection of scripts for playing with Bluesky on Diamond's Hardware Triggered Scanning Stack rigs.

============== ==============================================================
PyPI           ``pip install htss-rig-bluesky``
Source code    https://github.com/DiamondLightSource/htss-rig-bluesky
Documentation  https://DiamondLightSource.github.io/htss-rig-bluesky
Releases       https://github.com/DiamondLightSource/htss-rig-bluesky/releases
============== ==============================================================

Quickstart
----------

You can run an IPython terminal in a container with podman with access to a RunEngine 
and the Ophyd devices needed to control the test rig:

.. code:: shell

    export BEAMLINE=<the test rig you want to control, either p46, p47, p48 or p49>
    podman run -it --rm --net host -e BEAMLINE=${BEAMLINE} ghcr.io/diamondlightsource/htss-rig-bluesky:latest
    
Note that you must be on the same network as the test rig.
This should provide an IPython prompt, into which you can run a basic scan:

.. code:: IPython

    In [1]: RE(bp.scan([det], sample_stage.theta, 0.0, 180.0, 10))


.. |code_ci| image:: https://github.com/DiamondLightSource/htss-rig-bluesky/actions/workflows/code.yml/badge.svg?branch=main
    :target: https://github.com/DiamondLightSource/htss-rig-bluesky/actions/workflows/code.yml
    :alt: Code CI

.. |docs_ci| image:: https://github.com/DiamondLightSource/htss-rig-bluesky/actions/workflows/docs.yml/badge.svg?branch=main
    :target: https://github.com/DiamondLightSource/htss-rig-bluesky/actions/workflows/docs.yml
    :alt: Docs CI

.. |coverage| image:: https://codecov.io/gh/DiamondLightSource/htss-rig-bluesky/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/DiamondLightSource/htss-rig-bluesky
    :alt: Test Coverage

.. |pypi_version| image:: https://img.shields.io/pypi/v/htss-rig-bluesky.svg
    :target: https://pypi.org/project/htss-rig-bluesky
    :alt: Latest PyPI version

.. |license| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :target: https://opensource.org/licenses/Apache-2.0
    :alt: Apache License

..
    Anything below this line is used when viewing README.rst and will be replaced
    when included in index.rst

See https://DiamondLightSource.github.io/htss-rig-bluesky for more detailed documentation.
