#!/usr/bin/env python

from distutils.core import setup, Extension
from distutils.debug import DEBUG
import itertools
import sys
import platform
import os

mods = []

def find_MS_SDK():
    candidate_env_roots = 'ProgramFiles', 'ProgramFiles(x86)'
    candidate_roots = itertools.ifilter(None,
        itertools.imap(os.getenv, candidate_env_roots)
    )
    candidate_paths = (
        r'Microsoft SDKs\Windows\v6.0A', # Visual Studio 9
        r'Microsoft SDKs\Windows\v7.0A', # Visual Studio 10
        'Microsoft Platform SDK for Windows XP',
        'Microsoft Platform SDK',
    )
    candidate_pairs = itertools.product(candidate_roots, candidate_paths)
    candidates = itertools.starmap(os.path.join, candidate_pairs)
    matches = itertools.ifilter(os.path.exists, candidates)
    try:
        return matches.next()
    except StopIteration():
        pass

if sys.platform == 'win32':
    PSDK_PATH = find_MS_SDK()
    if PSDK_PATH is None:
        raise SystemExit("Could not find the Windows Platform SDK")

    lib_path = os.path.join(PSDK_PATH, 'Lib')
    if '64' in platform.architecture()[0]:
        lib_path = os.path.join(lib_path, 'x64')
    mod1 = Extension ('bluetooth._msbt',
                        include_dirs = ["%s\\Include" % PSDK_PATH],
                        library_dirs = [lib_path],
                        libraries = [ "WS2_32", "Irprops" ],
                        sources=['msbt\\_msbt.c'],)
    mods = [ mod1 ]

    # widcomm ?
    WC_BASE = os.path.join(os.getenv('ProgramFiles'), r"Widcomm\BTW DK\SDK")
    if os.path.exists (WC_BASE):
        mod2 = Extension ('bluetooth._widcomm',
                include_dirs = [ "%s\\Inc" % WC_BASE ],
                define_macros = [ ('_BTWLIB', None) ],
                library_dirs = [ "%s\\Release" % WC_BASE,
                                 "%s\\Lib" % PSDK_PATH, ],
                libraries = [ "WidcommSdklib", "ws2_32", "version", "user32", "Advapi32", "Winspool", "ole32", "oleaut32" ],
                sources = [ "widcomm\\_widcomm.cpp",
                            "widcomm\\inquirer.cpp",
                            "widcomm\\rfcommport.cpp",
                            "widcomm\\rfcommif.cpp",
                            "widcomm\\l2capconn.cpp",
                            "widcomm\\l2capif.cpp",
                            "widcomm\\sdpservice.cpp",
                            "widcomm\\util.cpp" ]
                )
        mods.append (mod2)

elif sys.platform.startswith('linux'):
    mod1 = Extension('bluetooth._bluetooth',
		                 libraries = ['bluetooth'],
                         sources = ['bluez/btmodule.c', 'bluez/btsdp.c'])
    mods = [ mod1 ]
elif sys.platform == 'darwin':
    mod1 = Extension('bluetooth._osxbt',
                     include_dirs = ["/System/Library/Frameworks/IOBluetooth.framework/Headers",
                     "/System/Library/Frameworks/CoreFoundation.framework/Headers"],
                     extra_link_args = ['-framework IOBluetooth -framework CoreFoundation'],
                     sources = ['osx/_osxbt.c']
                     )
    mods = [ mod1 ]
else:
    raise Exception("This platform (%s) is currently not supported by pybluez." % sys.platform)


setup (	name = 'PyBluez',
       	version = '0.19',
       	description = 'Bluetooth Python extension module',
       	author="Albert Huang",
     	author_email="ashuang@alum.mit.edu",
      	url="http://org.csail.mit.edu/pybluez",
       	ext_modules = mods,
        packages = [ "bluetooth" ],

# for the python cheese shop
        classifiers = [ 'Development Status :: 4 - Beta',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Programming Language :: Python',
            'Topic :: Communications' ],
        download_url = 'http://org.csail.mit.edu/pybluez/download.html',
        long_description = 'Bluetooth Python extension module to allow Python developers to use system Bluetooth resources. PyBluez works with GNU/Linux and Windows XP.',
        maintainer = 'Albert Huang',
        maintainer_email = 'ashuang@alum.mit.edu',
        license = 'GPL',
        )
