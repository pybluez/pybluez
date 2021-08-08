.. _installing:

Installing PyBluez
==================

PyBluez can be installed on GNU/Linux, Windows and macOS systems.

.. note:: Before you install **PyBluez** please install the dependencies required for
		  your system as described in the sections below.

**Installing PyBluez using pip**

Open a terminal (command prompt on Windows) and enter
::

	pip install pybluez

For experimental Bluetooth Low Energy support (only for Linux platform -
for additional dependencies please take look at:
`ble-dependencies <https://github.com/oscaracena/pygattlib/blob/master/DEPENDS>`_)
::

    pip install pybluez[ble]

**Installing PyBluez from source**

Download a stable release from `<https://github.com/pybluez/pybluez/releases>`_

or download the latest version using the links below.

+------+------+----------------+
| master.zip_ | master.tar.gz_ | 
+------+------+----------------+

.. _master.zip: https://github.com/pybluez/pybluez/archive/master.zip
.. _master.tar.gz: https://github.com/pybluez/pybluez/archive/master.tar.gz

Extract the zip or tar and cd to the extracted file directory, then:
::

	python setup.py install

for Bluetooth Low Energy support (GNU/Linux only):
::

    pip install -e .[ble]

GNU/Linux Dependencies
""""""""""""""""""""""

- Python 3.5 or newer
- Python distutils (standard in most Python distros, separate package python-dev in Debian)
- BlueZ libraries and header files (libbluetooth-dev)

Windows Dependencies
""""""""""""""""""""

- Windows 7/8/8.1/10
- Python 3.5 or newer

PyBluez requires a C++ compiler installed on your system to build CPython modules.

For Python 3.5 or higher

- Microsoft Visual C++ 14.0 standalone: Build Tools for Visual Studio 2017 (x86, x64, ARM, ARM64)
- Microsoft Visual C++ 14.0 with Visual Studio 2017 (x86, x64, ARM, ARM64)
- Microsoft Visual C++ 14.0 standalone: Visual C++ Build Tools 2015 (x86, x64, ARM)
- Microsoft Visual C++ 14.0 with Visual Studio 2015 (x86, x64, ARM)

.. note:: Windows 10 users need to download and install the `Windows 10 SDK <https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk>`_


`More details here <https://wiki.python.org/moin/WindowsCompilers>`_

- Widcomm BTW development kit 5.0 or later (Optional)

macOS Dependencies
"""""""""""""""""" 

- Xcode
- PyObjc 3.1b or later (https://pyobjc.readthedocs.io/en/latest/install.html)
