.. _api:

Application programming interface
=================================

This section of the documentation contains the PyBluez API (Application Programming Interface).
For most applications understanding use of the PyBluez common library is sufficient. 
For applications where operating system dependent functionality is required please
see the operating system specific pages.

Documentation for the Python objects defined by the project is divided into package, module, 
and class. 

Package: bluetooth
------------------
::

   >>> import bluetooth as bt

.. module:: bluetooth

Modules
~~~~~~~
When the bluetooth package is imported the appropriate operating system module is automatically
loaded in. This means application developers access the api classes and functions using the package
reference rather than the specific module.
::

   For example:

   >>> import bluetooth as bt
   >>> services = bt.find_service(address=None)

   Should work on all operating systems.

The modules are documented by operating system here purely as reference.

.. toctree::
	:maxdepth: 2

	api_bt_bluez
	api_bt_macos
	api_bt_ms
	api_bt_widcomm
	api_com


	



