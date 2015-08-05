#!/usr/bin/env python

from setuptools import setup, Extension
import sys
import platform
import os

mods = list()

def find_MS_SDK():
    candidate_roots = (os.getenv('ProgramFiles'), os.getenv('ProgramW6432'),
                       os.getenv('ProgramFiles(x86)'))

    if sys.version < '3.3':
        MS_SDK = r'Microsoft SDKs\Windows\v6.0A'  # Visual Studio 9
    else:
        MS_SDK = r'Microsoft SDKs\Windows\v7.0A'  # Visual Studio 10

    candidate_paths = (MS_SDK,
                       'Microsoft Platform SDK for Windows XP',
                       'Microsoft Platform SDK')

    for candidate_root in candidate_roots:
        for candidate_path in candidate_paths:
            candidate_sdk = os.path.join(candidate_root, candidate_path)
            if os.path.exists(candidate_sdk):
                return candidate_sdk

if sys.platform == 'win32':
    PSDK_PATH = find_MS_SDK()
    if PSDK_PATH is None:
        raise SystemExit("Could not find the Windows Platform SDK")

    lib_path = os.path.join(PSDK_PATH, 'Lib')
    if '64' in platform.architecture()[0]:
        lib_path = os.path.join(lib_path, 'x64')
    mods.append(Extension('bluetooth._msbt',
                          include_dirs=["%s\\Include" % PSDK_PATH, ".\\port3"],
                          library_dirs=[lib_path],
                          libraries=["WS2_32", "Irprops"],
                          sources=['msbt\\_msbt.c']))

    # widcomm
    WC_BASE = os.path.join(os.getenv('ProgramFiles'), r"Widcomm\BTW DK\SDK")
    if os.path.exists(WC_BASE):
        mods.append(Extension('bluetooth._widcomm',
                include_dirs=["%s\\Inc" % WC_BASE, ".\\port3"],
                define_macros=[('_BTWLIB', None)],
                library_dirs=["%s\\Release" % WC_BASE, "%s\\Lib" % PSDK_PATH],
                libraries=["WidcommSdklib", "ws2_32", "version", "user32",
                           "Advapi32", "Winspool", "ole32", "oleaut32"],
                sources=["widcomm\\_widcomm.cpp",
                         "widcomm\\inquirer.cpp",
                         "widcomm\\rfcommport.cpp",
                         "widcomm\\rfcommif.cpp",
                         "widcomm\\l2capconn.cpp",
                         "widcomm\\l2capif.cpp",
                         "widcomm\\sdpservice.cpp",
                         "widcomm\\util.cpp"]))

elif sys.platform.startswith('linux'):
    mods.append(Extension('bluetooth._bluetooth',
                          include_dirs=["./port3"],
                          libraries=['bluetooth'],
                          #extra_compile_args=['-O0'],
                          sources=['bluez/btmodule.c', 'bluez/btsdp.c']))
elif sys.platform == 'darwin':
    mods.append(Extension('bluetooth._osxbt',
                    include_dirs=["/System/Library/Frameworks/IOBluetooth.framework/Headers",
                    "/System/Library/Frameworks/CoreFoundation.framework/Headers"],
                    extra_link_args=['-framework IOBluetooth -framework CoreFoundation'],
                    sources=['osx/_osxbt.c']))
else:
    raise Exception("This platform (%s) is currently not supported by pybluez."
                    % sys.platform)


setup(name='PyBluez',
      version='0.22',
      description='Bluetooth Python extension module',
      author="Albert Huang",
      author_email="ashuang@alum.mit.edu",
      url="http://karulis.github.io/pybluez/",
      ext_modules=mods,
      packages=["bluetooth"],
# for the python cheese shop
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'Topic :: Communications'],
      download_url='https://github.com/karulis/pybluez',
      long_description='Bluetooth Python extension module to allow Python "\
                "developers to use system Bluetooth resources. PyBluez works "\
                "with GNU/Linux and Windows XP.',
      maintainer='Piotr Karulis',
      license='GPL',
      extras_require={'ble': ['gattlib==0.20150805']})
