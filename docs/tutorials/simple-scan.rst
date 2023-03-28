Run a Simple Scan
=================

Assuming you've followed the quickstart guide or otherwise got an IPython terminal to control a test rig...

.. code:: IPython

    In [1]: # Run a utility plan to ensure detector settings are sensible (num images, exposure time etc.)

    In [2]: RE(ensure_detector_ready(det))
    Out[2]: ()

    In [3]: # Run a scan

    In [4]: RE(bp.scan([det], sample_stage.theta, 0.0, 180.0, 10))


    Transient Scan ID: 1     Time: 2023-03-28 12:32:36
    Persistent Unique Scan ID: 'b3a246bc-5ba1-4d37-86d7-5071357f23db'
    New stream: 'primary'
    +-----------+------------+--------------------+
    |   seq_num |       time | sample_stage_theta |
    +-----------+------------+--------------------+
    |         1 | 12:32:36.8 |              0.000 |
    |         2 | 12:32:37.2 |             19.998 |
    |         3 | 12:32:37.6 |             39.996 |
    |         4 | 12:32:38.0 |             59.994 |
    |         5 | 12:32:38.4 |             79.992 |
    |         6 | 12:32:38.9 |            100.008 |
    |         7 | 12:32:39.3 |            120.006 |
    |         8 | 12:32:39.7 |            140.004 |
    |         9 | 12:32:40.1 |            160.002 |
    |        10 | 12:32:40.5 |            180.000 |
    +-----------+------------+--------------------+
    generator scan ['b3a246bc'] (scan num: 1)



    Out[4]: ('b3a246bc-5ba1-4d37-86d7-5071357f23db',)

    In [5]: 