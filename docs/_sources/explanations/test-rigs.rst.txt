Test Rigs
=========

The 4 tests rigs (P46, P47, P48 and P49) are virtually identical and model a very basic tomography beamline analogue.


Hardware Arrangement
--------------------

.. image:: ../images/rig-hardware.png
  :width: 800
  :alt: Software packages in the training room

The hardware consists of an X stage, a rotation stage and a detector. The detector can
image a backlit sample and the images can be used in visible light tomography.


Bluesky Control
---------------

Bluesky_ controls each IOC via Ophyd_ devices. The code for these can be
found in the Dodal_ repository. The Bluesky ``RunEngine`` runs on an external workstation.



.. _Bluesky: https://blueskyproject.io/bluesky/
.. _Ophyd: https://blueskyproject.io/ophyd/
.. _Dodal: https://github.com/DiamondLightSource/dodal