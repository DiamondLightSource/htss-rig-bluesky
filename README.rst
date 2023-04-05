htss-rig-bluesky
===========================

|code_ci| |docs_ci| |license|

Collection of scripts for playing with Bluesky on Diamond's Hardware Triggered Scanning Stack rigs.

============== ==============================================================
PyPI           ``pip install htss-rig-bluesky``
Source code    https://github.com/DiamondLightSource/htss-rig-bluesky
Documentation  https://DiamondLightSource.github.io/htss-rig-bluesky
Releases       https://github.com/DiamondLightSource/htss-rig-bluesky/releases
============== ==============================================================

Quickstart
----------

You can run an IPython terminal in a container via podman with access to a RunEngine 
and the Ophyd devices needed to control the test rig:

.. code:: shell

    export BEAMLINE=<the test rig you want to control, either p46, p47, p48 or p49>
    podman run -it --rm --net host -e BEAMLINE=${BEAMLINE} -e MINIMAL=1 ghcr.io/diamondlightsource/htss-rig-bluesky:latest
    
Note that you must be on the same network as the test rig.
This should provide an IPython prompt, into which you can run a basic scan:

.. code:: IPython

    In [1]: RE(bp.scan([det], sample_stage.theta, 0.0, 180.0, 10))


    Transient Scan ID: 1     Time: 2023-03-28 09:59:39
    Persistent Unique Scan ID: '57eb5122-a1e4-4c5f-b784-ded7656b6206'
    New stream: 'primary'
    +-----------+------------+--------------------+
    |   seq_num |       time | sample_stage_theta |
    +-----------+------------+--------------------+
    |         1 | 09:59:40.6 |              0.000 |
    |         2 | 09:59:41.0 |             19.998 |
    |         3 | 09:59:41.5 |             39.996 |
    |         4 | 09:59:41.9 |             60.012 |
    |         5 | 09:59:42.3 |             79.992 |
    |         6 | 09:59:42.7 |             99.990 |
    |         7 | 09:59:43.2 |            119.988 |
    |         8 | 09:59:43.6 |            140.004 |
    |         9 | 09:59:44.0 |            160.002 |
    |        10 | 09:59:44.4 |            180.000 |
    +-----------+------------+--------------------+
    generator scan ['57eb5122'] (scan num: 1)



    Out[1]: ('57eb5122-a1e4-4c5f-b784-ded7656b6206',)

    In [2]: 



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
