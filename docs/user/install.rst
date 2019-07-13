Installing PyBluez
==================

PyBluez can be installed on GNU/Linux, Windows and Mac operating systems and compatible 
with Python 2 and 3. 

.. note:: Before you install **PyBluez** please install the dependencies required for
		  your system as described in the sections below.

**Installing PyBluez using pip**
::

	pip install pybluez

**Installing PyBluez from source**

Download a stable release, or bleeding edge if you fancy the risk.

+------------+------------+---------------+
|Version 0.22| zip_v0.22_ | tar.gz_v0.22_ | 
+------------+------------+---------------+
|Version 0.21| zip_v0.21_ | tar.gz_v0.21_ | 
+------------+------------+---------------+

+-------------+------+---------+
|Bleeding Edge| zip_ | tar.gz_ | 
+-------------+------+---------+

Extract the zip or tar and cd to the extracted file directory, then:
::

	python setup.py install


**GNU/Linux Dependencies**

- Python 2.3 or more recent version
- Python distutils (standard in most Python distros, separate package python-dev in Debian)
- BlueZ libraries and header files

**Windows Dependencies**

- Microsoft Windows XP SP1 or Windows Vista/7/8/8.1
- Visual C++ 2010 Express for build for Python 3.3 or newer
- Visual C++ 2008 Express for build for Python 3.2 or older

- In order to build 64-bit debug and release executables, 
  Visual Studio 2008/2010 Standard Edition is required.

- Widcomm BTW development kit 5.0 or later (Optional)
- Python 2.3 or more recent version

**Mac OS Dependencies**

- Python 2.3 or later
- Xcode
- PyObjc 3.1b or later (https://pythonhosted.org/pyobjc/install.html#manual-installation)


.. _zip_v0.22: https://github.com/pybluez/pybluez/archive/0.22.zip
.. _tar.gz_v0.22: https://github.com/pybluez/pybluez/archive/0.22.tar.gz
.. _zip_v0.21: https://github.com/pybluez/pybluez/archive/0.21.zip
.. _tar.gz_v0.21: https://github.com/pybluez/pybluez/archive/0.21.tar.gz
.. _zip: https://github.com/pybluez/pybluez/archive/master.zip
.. _tar.gz: https://github.com/pybluez/pybluez/archive/master.tar.gz