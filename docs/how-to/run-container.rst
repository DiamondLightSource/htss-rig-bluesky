Run in a container
==================

Pre-built containers with htss-rig-bluesky and its dependencies already
installed are available on `Github Container Registry
<https://ghcr.io/DiamondLightSource/htss-rig-bluesky>`_.

Starting the container
----------------------

To pull the container from github container registry and run::

    $ docker run ghcr.io/DiamondLightSource/htss-rig-bluesky:main --version

To get a released version, use a numbered release instead of ``main``.
