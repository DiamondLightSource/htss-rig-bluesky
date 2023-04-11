Work with Devices
=================

.. note::

    Assuming you've followed the `quickstart guide <../index>` or otherwise got an IPython terminal to control a test rig...

There are objects provided that represent the hardware devices on the test rig, for example, the motors. The devices exist in a tree-like heirachy, 
so you can drill down into individual motors.

.. code:: IPython

    In [1]: sample_stage
    Out[1]: SampleStage(prefix='BL49P-MO-MAP-01:STAGE:', name='sample_stage', read_attrs=['x', 'x.user_readback', 'x.user_setpoint', 'theta', 'theta.user_readback', 'theta.user_setpoint'], configuration_attrs=['x', 'x.user_offset', 'x.user_offset_dir', 'x.velocity', 'x.acceleration', 'x.motor_egu', 'theta', 'theta.user_offset', 'theta.user_offset_dir', 'theta.velocity', 'theta.acceleration', 'theta.motor_egu'])

    In [2]: sample_stage.theta
    Out[2]: EpicsMotor(prefix='BL49P-MO-MAP-01:STAGE:A', name='sample_stage_theta', parent='sample_stage', settle_time=0.0, timeout=None, read_attrs=['user_readback', 'user_setpoint'], configuration_attrs=['user_offset', 'user_offset_dir', 'velocity', 'acceleration', 'motor_egu'])


You can call ``describe()`` on an Ophyd object to see what information can be recorded about it as beamline data.

.. code:: IPython

    In [3]: sample_stage.theta.describe()
    Out[3]: 
    OrderedDict([('sample_stage_theta',
                {'source': 'PV:BL49P-MO-MAP-01:STAGE:A.RBV',
                'dtype': 'number',
                'shape': [],
                'units': 'mm',
                'lower_ctrl_limit': 0.0,
                'upper_ctrl_limit': 0.0,
                'precision': 3}),
                ('sample_stage_theta_user_setpoint',
                {'source': 'PV:BL49P-MO-MAP-01:STAGE:A.VAL',
                'dtype': 'number',
                'shape': [],
                'units': 'mm',
                'lower_ctrl_limit': 0.0,
                'upper_ctrl_limit': 0.0,
                'precision': 3})])


There is a simple Bluesky plan for moving the motor:

.. code:: IPython

    In [4]: RE(bps.mv(sample_stage.theta, 0))
    Out[4]: ()

    In [5]: RE(bps.mv(sample_stage.theta, 360*5))
    Out[5]: ()


.. note:: ``RE`` refers to the Bluesky ``RunEngine``, which executes plans and does the actual talking to hardware.


``mv()`` can move multiple motors simultaneously too:

.. code:: IPython

    In [6]: RE(bps.mv(sample_stage.theta, -360*5, sample_stage.x, 0))
    Out[6]: ()
