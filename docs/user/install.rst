
******************
Installing PyBluez
******************

PyBluez can be installed on GNU/Linux, Windows and macOS systems and is currently compatible 
with Python 2 and 3. 

.. important:: Python 2 reaches End of Life on January 1st 2020. As a consequence we are not
               actively maintaining PyBluez for this version of python. PyBluez v0.22 will still work 
               on python 2 however this may not be the case for future releases. We therefore encourage
               our users to consider transitioning to a python 3 version.  

.. note:: Before you install **PyBluez** please install the dependencies required for
		  your system as described in the sections below.

**Installing PyBluez using pip**
::

	pip install pybluez

**Installing PyBluez from source**

Download a stable release from `<https://github.com/pybluez/pybluez/releases>`_

or download the latest version using the links below.

+------+------+----------------+
| master.zip_ | master.tar.gz_ | 
+------+------+----------------+

Extract the zip or tar and cd to the extracted file directory, then:
::

	python setup.py install


GNU/Linux Dependencies
""""""""""""""""""""""

- Python 3.6 or more recent version
- Python distutils (standard in most Python distros, separate package python-dev in Debian)
- BlueZ libraries and header files

Windows Dependencies
""""""""""""""""""""

- Microsoft Windows XP SP1, Windows Vista/7/8/8.1/10

.. important:: PyBluez no longer provides maintenance or support for Windows XP. 

PyBluez requires a C++ compiler installed on your system to build CPython modules.

For Python 3.5 or higher

- Microsoft Visual C++ 14.0 standalone: Build Tools for Visual Studio 2017 (x86, x64, ARM, ARM64)
- Microsoft Visual C++ 14.0 with Visual Studio 2017 (x86, x64, ARM, ARM64)
- Microsoft Visual C++ 14.0 standalone: Visual C++ Build Tools 2015 (x86, x64, ARM)
- Microsoft Visual C++ 14.0 with Visual Studio 2015 (x86, x64, ARM)


`More details here <https://wiki.python.org/moin/WindowsCompilers>`_

- Widcomm BTW development kit 5.0 or later (Optional)
- Python 3.5 or more recent version


macOS Dependencies
"""""""""""""""""" 
- Xcode
- PyObjc 3.1b or later (https://pythonhosted.org/pyobjc/install.html#manual-installation)



.. _master.zip: https://github.com/pybluez/pybluez/archive/master.zip
.. _master.tar.gz: https://github.com/pybluez/pybluez/archive/master.tar.gz


