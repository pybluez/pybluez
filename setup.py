#!/usr/bin/env python

from setuptools import setup, Extension
import sys
import platform
import os

packs = ['bluetooth']
pack_dir = dict()
mods = list()
install_req = list()


def find_MS_SDK():
    candidate_roots = (os.getenv('ProgramFiles'), os.getenv('ProgramW6432'),
                       os.getenv('ProgramFiles(x86)'))

    candidate_paths = []

    if sys.version_info[0:2] == (2, 7):
        # Microsoft Visual C++ Compiler for Python 2.7
        # https://www.microsoft.com/en-us/download/details.aspx?id=44266
        candidate_paths.append(r'Common Files\Microsoft\Visual C++ for Python\9.0\WinSDK')

    # Microsoft SDKs
    if sys.version < '3.3':
        candidate_paths.append(r'Microsoft SDKs\Windows\v6.0A')  # Visual Studio 9
    elif '3.3' <= sys.version < '3.5':
        candidate_paths.append(r'Microsoft SDKs\Windows\v7.0A')  # Visual Studio 10
    elif sys.version >= '3.5':
        candidate_paths.append(r'Microsoft SDKs\Windows\v10.0A')  # Visual Studio 14

    candidate_paths.extend((
        'Microsoft Platform SDK for Windows XP',
        'Microsoft Platform SDK'
    ))

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
    mod1 = Extension('bluetooth._bluetooth',
                        include_dirs = ["./port3",],
                        libraries = ['bluetooth'],
                        #extra_compile_args=['-O0'],
                        sources = ['bluez/btmodule.c', 'bluez/btsdp.c'])
    mods = [ mod1 ]

elif sys.platform.startswith("darwin"):
    # On Mac, install LightAquaBlue framework
    # if you want to install the framework somewhere other than /Library/Frameworks
    # make sure the path is also changed in LightAquaBlue.py (in src/mac)
    packs.append('lightblue')
    pack_dir = { 'lightblue': 'osx' }
    if "install" in sys.argv:
        install_req = ['pyobjc-core>=3.1', 'pyobjc-framework-Cocoa>=3.1']
        # Change to LightAquaBlue framework dir.
        os.chdir("osx/LightAquaBlue")

        #
        # NOTE: our solution is based on these posts:
        #  - http://stackoverflow.com/questions/22279913/how-to-install-either-pybluez-or-lightblue-on-osx-10-9-mavericks
        #  - https://github.com/0-1-0/lightblue-0.4/issues/7
        # We need to verify that the arch(itecture) param is specified accurately 
        # otherwise the compilation will fail.
        #
        arch = None
        if "NATIVE_ARCH_ACTUAL" in os.environ:
            arch = "$(NATIVE_ARCH_ACTUAL)"
        elif "64bit" in platform.architecture():
            arch = "x86_64"
        elif "32bit" in platform.architecture():
            arch = "i386"
        else:
            raise Exception("Unrecognized architecture")

        build_str = "xcodebuild install -arch '%s' -target LightAquaBlue -configuration Release DSTROOT=/ INSTALL_PATH=/Library/Frameworks DEPLOYMENT_LOCATION=YES" % (arch)
        os.system(build_str)

        # Change back to top-level (need this otherwise setup.py script gets confused on install?).
        os.chdir("../..")

        mods = []
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
      packages=packs,
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
      extras_require={'ble': ['gattlib==0.20150805']},
      package_dir=pack_dir,
      use_2to3=True,
      install_requires=install_req)
