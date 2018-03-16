#!/usr/bin/env python

from setuptools import setup, Extension
import sys
import platform
import os

packages = ['bluetooth']
package_dir = dict()
ext_modules = list()
install_requires = list()
package_data = dict()
eager_resources = list()
zip_safe = True


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
    ext_modules.append(Extension('bluetooth._msbt',
                          include_dirs=["%s\\Include" % PSDK_PATH, ".\\port3"],
                          library_dirs=[lib_path],
                          libraries=["WS2_32", "Irprops"],
                          sources=['msbt\\_msbt.c']))

    # widcomm
    WC_BASE = os.path.join(os.getenv('ProgramFiles'), r"Widcomm\BTW DK\SDK")
    if os.path.exists(WC_BASE):
        ext_modules.append(Extension('bluetooth._widcomm',
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
    ext_modules.append(mod1)

elif sys.platform.startswith("darwin"):
    packages.append('lightblue')
    package_dir['lightblue'] = 'macos'
    install_requires += ['pyobjc-core>=3.1', 'pyobjc-framework-Cocoa>=3.1']
    zip_safe = False
    
    # FIXME: This is inelegant, how can we cover the cases?
    if 'install' in sys.argv or 'bdist' in sys.argv or 'bdist_egg' in sys.argv:
        # Build the framework into macos/
        import subprocess
        subprocess.check_call([
            'xcodebuild', 'install',
            '-project', 'macos/LightAquaBlue/LightAquaBlue.xcodeproj',
            '-scheme', 'LightAquaBlue',
            'DSTROOT=' + os.path.join(os.getcwd(), 'macos'),
            'INSTALL_PATH=/',
            'DEPLOYMENT_LOCATION=YES',
        ])
        
        # We can't seem to list a directory as package_data, so we will
        # recursively add all all files we find
        package_data['lightblue'] = []
        for path, _, files in os.walk('macos/LightAquaBlue.framework'):
            for f in files:
                include = os.path.join(path, f)[6:]  # trim off macos/
                package_data['lightblue'].append(include)
    
        # This should allow us to use the framework from an egg [untested]
        eager_resources.append('macos/LightAquaBlue.framework')
        
else:
    raise Exception("This platform (%s) is currently not supported by pybluez."
                    % sys.platform)


setup(name='PyBluez',
      version='0.22',
      description='Bluetooth Python extension module',
      author="Albert Huang",
      author_email="ashuang@alum.mit.edu",
      url="http://pybluez.github.io/",
      ext_modules=ext_modules,
      packages=packages,
# for the python cheese shop
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'Topic :: Communications'],
      download_url='https://github.com/pybluez/pybluez',
      long_description='Bluetooth Python extension module to allow Python "\
                "developers to use system Bluetooth resources. PyBluez works "\
                "with GNU/Linux, macOS, and Windows XP.',
      maintainer='Piotr Karulis',
      license='GPL',
      extras_require={'ble': ['pygattlib==0.0.3']},
      package_dir=package_dir,
      use_2to3=True,
      install_requires=install_requires,
      package_data=package_data,
      eager_resources=eager_resources,
      zip_safe=zip_safe)
