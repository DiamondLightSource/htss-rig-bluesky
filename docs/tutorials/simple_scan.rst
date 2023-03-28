Run a Simple Scan
=================

Assuming you've followed the quickstart guide or otherwise got an IPython terminal to control a test rig...

.. code:: IPython

    [1]: # Run a utility plan to ensure detector settings are sensible (num images, exposure time etc.)
    [2]: RE(setup_detector(det))
    [3]: # Run a scan
    [4]: RE(bp.scan([det], sample_stage.theta, 0.0, 180.0, 10))
