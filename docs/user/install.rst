******************
Installing PyBluez
******************

PyBluez can be installed on GNU/Linux, Windows and macOS systems and is compatible 
with Python 2.7 and 3. 

.. note:: Before you install **PyBluez** please install the dependencies required for
		  your system as described in the sections below.

**Installing PyBluez using pip**
::

	pip install pybluez

(there are also binaries for Windows platform on PyPI or here - `Unofficial Windows Binaries for Python Extension Packages <https://www.lfd.uci.edu/~gohlke/pythonlibs/#pybluez>`)

For experimental Bluetooth Low Energy support (only for Linux platform -
for additional dependencies please take look at:
`ble-dependencies <https://bitbucket.org/OscarAcena/pygattlib/src/45e04060881a20189412681f52d55ff5add9f388/DEPENDS?at=default>`)
::

    pip install pybluez\[ble\]

**Installing PyBluez from source**

Download a stable release from `<https://github.com/pybluez/pybluez/releases>`_

or download the latest version using the links below.

+------+------+----------------+
| master.zip_ | master.tar.gz_ | 
+------+------+----------------+

Extract the zip or tar and cd to the extracted file directory, then:
::

	python setup.py install

for Bluetooth Low Energy support (GNU/Linux only):
::

    pip install -e .\[ble\]

GNU/Linux Dependencies
""""""""""""""""""""""

- Python 2.7 or more recent version
- Python distutils (standard in most Python distros, separate package python-dev in Debian)
- BlueZ libraries and header files

Windows Dependencies
""""""""""""""""""""

- Microsoft Windows XP SP1, Windows Vista/7/8/8.1/10

PyBluez requires a C++ compiler installed on your system to build CPython modules.

For Python 3.5 or higher

- Microsoft Visual C++ 14.0 standalone: Build Tools for Visual Studio 2017 (x86, x64, ARM, ARM64)
- Microsoft Visual C++ 14.0 with Visual Studio 2017 (x86, x64, ARM, ARM64)
- Microsoft Visual C++ 14.0 standalone: Visual C++ Build Tools 2015 (x86, x64, ARM)
- Microsoft Visual C++ 14.0 with Visual Studio 2015 (x86, x64, ARM)

For Python 3.3 or 3.4

- Microsoft Visual C++ 10.0 standalone: Windows SDK 7.1 (x86, x64, ia64)
- Microsoft Visual C++ 10.0 with Visual Studio 2010 (x86, x64, ia64)

For Python 2.7, 3.0, 3.1, 3.2

- Microsoft Visual C++ 9.0 standalone: Visual C++ Compiler for Python 2.7 (x86, x64)
- Microsoft Visual C++ 9.0 standalone: Windows SDK 7.0 (x86, x64, ia64)
- Microsoft Visual C++ 9.0 standalone: Windows SDK 6.1 (x86, x64, ia64)
- Microsoft Visual C++ 9.0 with Visual Studio 2008 (x86, x64, ia64)

`More details here <https://wiki.python.org/moin/WindowsCompilers>`_

- Widcomm BTW development kit 5.0 or later (Optional)
- Python 2.7 or more recent version


macOS Dependencies
"""""""""""""""""" 
- Xcode
- PyObjc 3.1b or later (https://pythonhosted.org/pyobjc/install.html#manual-installation)



.. _master.zip: https://github.com/pybluez/pybluez/archive/master.zip
.. _master.tar.gz: https://github.com/pybluez/pybluez/archive/master.tar.gz
