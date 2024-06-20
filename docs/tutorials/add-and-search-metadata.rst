Add and Search Through Metadata
===============================

.. note::

    Requires `./access-data`


Bluesky supports rich metadata and good indexing and searching via databroker.

Try running the following series of commands in IPython:

.. code:: shell

    RE(bp.scan([det], sample_stage.theta, 0, 180, 10, md={"for_user": "George"}))
    RE(bp.scan([det], sample_stage.theta, 0, 180, 10, md={"for_user": "Beth"}))
    RE(bp.scan([det], sample_stage.theta, 0, 180, 10, md={"for_user": "George"}))
    RE(bp.scan([det], sample_stage.theta, 0, 180, 10, md={"for_user": "Beth"}))
    RE(bp.scan([det], sample_stage.theta, 0, 180, 10, md={"for_user": "Amy"}))
    RE(bp.scan([det], sample_stage.theta, 0, 180, 10, md={"for_user": "George"}))
    RE(bp.scan([det], sample_stage.theta, 0, 180, 10, md={"for_user": "Beth"}))

Bluesky will produce events associated with this scan and include a piece of custom 
metadata in each event.

You can then used Tiled to search for scans with certain metadata, for example

.. code:: IPython

    In [21]: all_scans_for_beth = tiled.search(Key("for_user") == "Beth")

    In [22]: list(all_scans_for_beth)
    Out[22]: 
    ['8e8a2dee-c600-44d4-9856-86de449654ad',
    'b065d8bf-12c1-46a5-90a0-d0c54c057cc4',
    '6ad60b88-d1b1-4a8f-8652-709f86b03da5',
    '0a7023d3-bd1d-487a-b78d-68fc5777a483']

    In [23]: all_scans_for_beth[-1].primary.read()
    Out[23]: 
    <xarray.Dataset>
    Dimensions:                           (time: 10, dim_0: 1, dim_1: 20,
                                        dim_2: 1272)
    Coordinates:
    * time                              (time) float64 1.686e+09 ... 1.686e+09
    Dimensions without coordinates: dim_0, dim_1, dim_2
    Data variables:
        sample_stage_theta                (time) float64 0.0 20.0 ... 160.0 180.0
        sample_stage_theta_user_setpoint  (time) float64 0.0 20.0 ... 160.0 180.0
        det_cam_acquire_period            (time) float64 0.35 0.35 ... 0.35 0.35
        det_cam_acquire_time              (time) float64 0.15 0.15 ... 0.15 0.15
        det_image                         (time, dim_0, dim_1, dim_2) float64 145...
    Attributes:
        stream_name:  primary


Retireve all scans marked for "Beth", display their IDs and then display a 
detailed summary of the most recent one.

.. seealso:: `../explanations/data-access`
