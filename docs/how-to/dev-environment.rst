Setup Development Environment
=============================

These instructions will take you through the minimal steps required to get a dev
environment setup, so you can run the tests locally.

Clone the repository
--------------------

.. note::

    On a DLS machine, this should not be done in your home directory. ``/scratch/<your fedid>`` is recommended for speed. ``/dls/science/users/<your fedid>/`` is recommended for portability. You should also ensure your disk quota has space remaining, you can check with ``quota -s`` on the terminal.


First clone the repository locally using `Git
<https://git-scm.com/downloads>`_::

    $ git clone git@github.com:DiamondLightSource/htss-rig-bluesky.git


Install dependencies
--------------------

You can choose to either develop on the host machine using a `venv` (which
requires python 3.9 or later) or to run in a container under `VSCode
<https://code.visualstudio.com/>`_

.. tab-set::

    .. tab-item:: VSCode devcontainer (recommended)

        .. code:: shell

            module load vscode
            code htss-rig-bluesky
        
        Then see the `epics-containers instructions`_ for setting up a development container.

    .. tab-item:: Local virtualenv

        .. code:: shell

            cd htss-rig-bluesky
            python3.9 -m venv venv
            source venv/bin/activate
            pip install -e '.[dev]'

See what was installed
----------------------

To see a graph of the python package dependency tree type:

.. code:: shell
    
    pipdeptree

Build and test
--------------

Now you have a development environment you can run the tests in a terminal:

.. code:: shell

    tox -p

You can also run the IPython environment with 

.. code:: shell

    htss


.. _`epics-containers instructions`: https://epics-containers.github.io/main/user/tutorials/devcontainer.html
