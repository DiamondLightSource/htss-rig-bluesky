Check the Test Rig is in Working Order
======================================

.. note::

    Assuming you've followed the `quickstart guide <../index>` or otherwise got an IPython terminal to control a test rig...


There are a series of plans for exercising the test rig, which 
assert that the hardware and Ophyd devices are behaving as expected.

.. code:: IPython

    In [1]: RE(excercise_beamline(det, sample_stage))
    Excercising sample_stage_x
    Excercising sample_stage_theta
    Excercising AdAravisDetector(prefix='BL46P-EA-DET-01:', name='det', read_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'hdf'], configuration_attrs=['cam', 'cam.acquire_period', 'cam.acquire_time', 'cam.image_mode', 'cam.manufacturer', 'cam.model', 'cam.num_exposures', 'cam.num_images', 'cam.trigger_mode', 'hdf'])


    Transient Scan ID: 3     Time: 2023-04-04 13:34:07
    Persistent Unique Scan ID: '09f5ce67-adb6-46ab-a2ed-9779f01a80b9'
    /venv/lib/python3.10/site-packages/dodal/devices/areadetector/adutils.py:35: UserWarning: .dispatch is deprecated, use .generate_datum instead
    self.dispatch(self._image_name, ttime.time())
    New stream: 'primary'
    +-----------+------------+
    |   seq_num |       time |
    +-----------+------------+
    |         1 | 13:34:07.7 |
    +-----------+------------+
    generator count ['09f5ce67'] (scan num: 3)



    Excercising scan


    Transient Scan ID: 4     Time: 2023-04-04 13:34:08
    Persistent Unique Scan ID: '2bde468e-00ff-48e3-8c22-4c457e890509'
    New stream: 'primary'
    +-----------+------------+--------------------+
    |   seq_num |       time | sample_stage_theta |
    +-----------+------------+--------------------+
    |         1 | 13:34:10.2 |           -180.000 |
    |         2 | 13:34:10.8 |           -140.004 |
    |         3 | 13:34:11.3 |           -100.008 |
    |         4 | 13:34:11.8 |            -59.994 |
    |         5 | 13:34:12.3 |            -19.998 |
    |         6 | 13:34:12.9 |             19.998 |
    |         7 | 13:34:13.4 |             59.994 |
    |         8 | 13:34:13.9 |             99.990 |
    |         9 | 13:34:14.4 |            140.004 |
    |        10 | 13:34:15.0 |            180.000 |
    +-----------+------------+--------------------+
    generator scan ['2bde468e'] (scan num: 4)



    Out[3]: 
    ('09f5ce67-adb6-46ab-a2ed-9779f01a80b9',
    '2bde468e-00ff-48e3-8c22-4c457e890509')


.. note::

    The test rig hardware is not production quality and may occasionally behave inconsistently. If the exercises fail, it may be worth trying them again a couple of times.
 
