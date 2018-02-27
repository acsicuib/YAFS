============
Installation
============

YAFS is implemented in pure Python and has some dependencies. YAFS runs on Python 2 (>=2.7). PyPy is also supported. If you
have `pip <http://pypi.python.org/pypi/pip>`_ installed, just type

.. code-block:: bash

   $ pip install yafs


YAFS dependencies
=================


* NetworkX (2.0) for manipulate the topology
* Pandas (0.18.0) for obtaining stats
* Simpy (3.0.10) the discrete-event simulator
* TinyDB (3.7.0) a nosql database for stats records

You can use whatever python manager package for the installation of these libraries

We want to thank the contributors of these projects for their enormous work as well as the authors et al. of Simpy simulator. YAFS efficiency relies mainly on Simpy project.