Setup Development Environment
=============================

These instructions will take you through the minimal steps required to get a dev
environment setup, so you can run the tests locally.

Clone the repository
--------------------

First clone the repository locally using `Git
<https://git-scm.com/downloads>`_::

    $ git clone git@github.com:DiamondLightSource/htss-rig-bluesky.git

.. note::

    On a DLS machine, this should not be done in your home directory
 

Install dependencies
--------------------

You can choose to either develop on the host machine using a `venv` (which
requires python 3.8 or later) or to run in a container under `VSCode
<https://code.visualstudio.com/>`_

.. tab-set::

    .. tab-item:: VSCode devcontainer (recommended)

        .. code:: shell

            module load vscode
            code htss-rig-bluesky
        
            # Click on 'Reopen in Container' when prompted
            # Open a new terminal

    .. tab-item:: Local virtualenv

        .. code:: shell

            cd htss-rig-bluesky
            python3.8 -m venv venv
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
