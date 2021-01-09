#!/usr/bin/env python
import os
import platform
import sys

from setuptools import setup, Extension
from setuptools.dist import Distribution

# This marks the wheel as always being platform-specific and not pure Python
# See: https://stackoverflow.com/a/62668026
# Multiple inheritance to work around py27 problem with super(), see https://stackoverflow.com/a/18392639
class BinaryDistribution(Distribution, object):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(self):
        """We always have external modules"""
        return True

    def run_command(self, command):
        """patched to disallow the install without having built lightblue on osx"""
        if command == "install" and sys.platform.startswith("darwin"):
            if not self.package_data.get("lightblue"):
                raise RuntimeError("Build wheel first")
        return super(BinaryDistribution, self).run_command(command)


packages = ['bluetooth']
package_dir = dict()
ext_modules = list()
install_requires = list()
package_data = dict()
eager_resources = list()
zip_safe = True


if sys.platform == 'win32':
    ext_modules.append(Extension('bluetooth._msbt',
                       libraries=["WS2_32", "Bthprops"],
                       sources=['msbt\\_msbt.c']))

    # widcomm
    WC_BASE = os.path.join(os.getenv('ProgramFiles'), r"Widcomm\BTW DK\SDK")
    if os.path.exists(WC_BASE):
        ext_modules.append(Extension('bluetooth._widcomm',
                include_dirs=["%s\\Inc" % WC_BASE],
                define_macros=[('_BTWLIB', None)],
                library_dirs=["%s\\Release" % WC_BASE],
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
                     libraries = ['bluetooth'],
                     #extra_compile_args=['-O0'],
                     sources = ['bluez/btmodule.c', 'bluez/btsdp.c'])
    ext_modules.append(mod1)

elif sys.platform.startswith("darwin"):
    packages.append('lightblue')
    package_dir['lightblue'] = 'macos'
    zip_safe = False

    if sys.version_info >= (3,6):
        install_requires += ['pyobjc-core>=6', 'pyobjc-framework-Cocoa>=6']
    else:
        install_requires += ['pyobjc-core>=3.1,<6', 'pyobjc-framework-Cocoa>=3.1,<6']

    # FIXME: This is inelegant, how can we cover the cases?
    build_cmds = {'bdist', 'bdist_egg', 'bdist_wheel'}
    if build_cmds & set(sys.argv):
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
      version='0.30',
      description='Bluetooth Python extension module',
      author="Albert Huang",
      author_email="ashuang@alum.mit.edu",
      url="http://pybluez.github.io/",
      ext_modules=ext_modules,
      packages=packages,
      python_requires=">=3.5",
# for the python cheese shop
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Programming Language :: Python :: 3 :: Only',
                   'Topic :: Communications'],
      download_url='https://github.com/pybluez/pybluez',
      long_description='Bluetooth Python extension module to allow Python '\
                'developers to use system Bluetooth resources. PyBluez works '\
                'with GNU/Linux, macOS, and Windows.',
      maintainer='Piotr Karulis',
      license='GPL',
      extras_require={'ble': ['gattlib']},
      package_dir=package_dir,
      use_2to3=True,
      install_requires=install_requires,
      package_data=package_data,
      eager_resources=eager_resources,
      zip_safe=zip_safe,
      distclass=BinaryDistribution,
)
