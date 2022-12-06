python-can-sontheim
====================
|release| |python_implementation| |coverage| |downloads|

.. |release| image:: https://img.shields.io/pypi/v/python-can-sontheim.svg
   :target: https://pypi.python.org/pypi/python-can-sontheim/
   :alt: Latest Version on PyPi

.. |python_implementation| image:: https://img.shields.io/pypi/implementation/python-can-sontheim
   :target: https://pypi.python.org/pypi/python-can-sontheim/
   :alt: Supported Python implementations
   
.. |downloads| image:: https://pepy.tech/badge/python-can-sontheim
   :target: https://pepy.tech/project/python-can-sontheim
   :alt: Downloads on PePy
   
.. |coverage| image:: https://coveralls.io/repos/github/MattWoodhead/python-can-sontheim/badge.svg?branch=main
   :target: https://coveralls.io/github/MattWoodhead/python-can-sontheim?branch=main


This module is a plugin for the python-can_. module, that allows the use of CAN interfaces that rely on the Sontheim Industrie Elektronik (SIE) MTAPI drivers (windows only). These include the SIE CANfox (including rebranded versions such as that by IFM), SIE CANUSB, etc.


Installation
------------

Install using pip::

    $ pip install python-can-sontheim


Usage
-----

In general, useage is largely the same as with the main python-can_ library, using the interface designation of "sontheim". When integrating the sontheim interface into scripts, it is possible to import constants, device deisgnations etc from the python-can-sontheim module using "import can_sontheim". For the majority of the use cases, using an SIE interface is as simple as amending any python-can examples with the lines shown below:

Create python-can bus with the SIE CANfox USB interface:

.. code-block:: python

    import can
    from can_sontheim import devices

    bus = can.Bus(interface="sontheim", channel=devices.CANfox.CAN1, bitrate=250000, echo=False)

Some examples are present in the python-can-sontheim/examples_ directory in the repository, and more complete documentation specific to the SIE interfaces and driver will be uploaded to this module in due course.


.. _python-can: https://python-can.readthedocs.org/en/stable/

.. _examples: https://github.com/MattWoodhead/python-can-sontheim/tree/main/examples
