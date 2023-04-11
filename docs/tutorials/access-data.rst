Access Data
===========

Data access is enabled by removing the ``MINIMAL=1`` variable from your environment. 
For example, start a container with:

.. code:: shell

    podman run -it \
               --rm \
               --net host \
               -e BEAMLINE=${BEAMLINE} \
               -e DISPLAY=${DISPLAY} \
               --security-opt=label=type:container_runtime_t \
               ghcr.io/diamondlightsource/htss-rig-bluesky:latest

You may be prompted for a username and password to access data from the test rig. They are written on the top of the rig in question.

Data is supplied through Tiled_ with a Databroker_ plugin. The Tiled datasets can be viewed like Intake_ catalogs.
The latest run in the catalog (-1) may be "read" and the data retrieved and plotted.

.. code:: IPython

    In [1]: tiled
    Out[1]: <Catalog {1, 1, 2, 3, 4, 1, 1, 1, 2, 3, ...} ~25 entries>

.. note::

    It may say the catalog is empty, if so you can re-run the scan from the `quickstart guide <../index>` 
    to generate some data. 


You can retrieve data from the latest run with ``tiled[-1]``:

.. code:: IPython

    In [2]: ds = tiled[-1].primary.read()

    In [3]: ds["det_image"][0].plot()
    Out[3]: <matplotlib.collections.QuadMesh at 0x7fc480119930>

    In [4]: plt.show()


.. seealso:: `../explanations/data-access`


.. _Tiled: https://blueskyproject.io/tiled/
.. _Databroker: https://blueskyproject.io/databroker/
.. _Intake: https://pypi.org/project/intake/
