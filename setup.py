#!/usr/bin/env python

from distutils.core import setup, Extension
from distutils.debug import DEBUG
import sys
import os

mods = []

if sys.platform == 'win32':
    XP2_PSDK_PATH = os.path.join(os.getenv('ProgramFiles'), r"Microsoft Platform SDK for Windows XP SP2")
    S03_PSDK_PATH = os.path.join(os.getenv('ProgramFiles'), r"Microsoft Platform SDK")
    PSDK_PATH = None
    for p in [ XP2_PSDK_PATH, S03_PSDK_PATH ]:
        if os.path.exists(p):
            PSDK_PATH = p
            break
    if PSDK_PATH is None:
        raise SystemExit ("Can't find the Windows XP Platform SDK")
    
    mod1 = Extension ('bluetooth._msbt', 
                        include_dirs = ["%s\\Include" % PSDK_PATH],
                        library_dirs = ["%s\\Lib" % PSDK_PATH],
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
                libraries = [ "WidcommSdklib", "ws2_32", "version", "user32", "Advapi32", "Winspool", "ole32" ],
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
    
elif sys.platform == 'linux2':
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


setup (	name = 'PyBluez',
       	version = '0.16',
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
