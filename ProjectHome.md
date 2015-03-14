PyBluez is an effort to create python wrappers around system Bluetooth resources to allow Python developers to easily and quickly create Bluetooth applications.

PyBluez works on GNU/Linux and Windows XP (Microsoft and Widcomm Bluetooth stacks). It is freely available under the GNU General Public License.

## Documentation ##

See the [Documentation](Documentation.md) page.

## Mailing List / Contact ##

Please use the mailing list at http://groups.google.com/group/pybluez/

## News ##


#### Jan 19, 2014 ####

Version 0.20 released. No new features, just port to python 3.3.

#### Oct 15, 2009 ####

Version 0.17 released.  This is a bugfix release, affecting GNU/Linux only.  See the CHANGELOG for more details.

#### Feb 5, 2009 ####

Version 0.16 released.  This is a bugfix release, affecting both GNU/Linux and Windows.  See the CHANGELOG for more details.

#### Jan 21, 2008 ####

Version 0.15 released.  This is a bugfix release, affecting both GNU/Linux and Windows.  See the CHANGELOG for more details.

#### Jan 3, 2008 ####

We are slowly transitioning the website from MIT (org.csail.mit.edu/pybluez) to Google Code (http://pybluez.googlecode.com).  All new software releases will now be hosted on google code.

#### Nov 12, 2007 ####
Version 0.14 released. This is a bugfix release only, affecting only GNU/Linux. See the CHANGELOG for more details.

#### Aug 30, 2007 ####
Version 0.13 released. This is a bugfix release only, affecting only GNU/Linux. See the CHANGELOG for more details.

#### Aug 29, 2007 ####
Version 0.12 released. This is a bugfix release only, affecting only GNU/Linux. See the CHANGELOG for more details.

#### Aug 25, 2007 ####
Version 0.11 released. This is a bugfix release only, affecting only MS Windows see the CHANGELOG for more details.

#### Aug 15, 2007 ####
Version 0.10 released. Big news this time is that I've added support for the Widcomm stack in Windows XP. This is not well tested and very experimental at this point, so bug reports are appreciated. From the CHANGELOG:
```
    added experimental Broadcom/Widcomm support.  All the basics should be
    supported:
        RFCOMM sockets
        L2CAP sockets
        Device Discovery, Name Lookup
        SDP search on remote devices
        SDP advertisement (RFCOMM, L2CAP)

    Widcomm stack notes:
        1. BluetoothSocket.accept () always returns 0 for the port,
           as the RFCOMM channel/L2CAP PSM of the client device is not exposed
           by the Widcomm API
        2. Not all fields of advertise_service are supported.  The following
           parameters are currently not supported:
               description, protocols
        3. The following methods of BluetoothSocket are not supported:
              gettimeout, dup, makefile, settimeout
        4. The following parameters to discover_devices are not supported:
               duration, flush_cache (cache always flushes)
        5. The timeout parameter of lookup_name is not supported
        6. Once a listening socket has accepted a connection, it is not put
           back into listening mode.  The original listening socket essentially
           becomes useless.
        7. SDP search/browse operations on the local host are not yet supported
```

#### Dec 27, 2006 ####
Version 0.9.2 released. Fixed an endian-error that affects L2CAP sockets on big-endian machines only.

#### Sep 14, 2006 ####
Version 0.9.1 released. Fixed a missing #include that prevented PyBluez from compiling with new versions of BlueZ

#### Sep 1, 2006 ####
Version 0.9 released. Bug fixes and minor functionality improvements. See the CHANGELOG for details.

#### July 31, 2006 ####
Version 0.8 released. Bug fix for Linux and minor functionality improvements for Windows XP. See the CHANGELOG for details.

#### May 13, 2006 ####
Version 0.7.1 released. Bug fixes and minor functionality improvements for Windows XP. See the CHANGELOG for more details. Code examples and documentation on this website should be up to date now.

#### May 5, 2006 ####
Version 0.7 released. Support added for Windows XP. See the CHANGELOG for more details. The documentation on this website is now a little out of date, see the examples included in the source distributions for... examples. Web documentation will hopefully be updated soon.

#### Mar 20, 2006 ####
PyBluez is now available in Debian unstable as package python-bluez. .deb binaries will no longer be distributed from this page for future releases. To obtain them, either use Debian or download from http://packages.debian.org.

#### Feb 24, 2006 ####
Version 0.6.1 released. Last week's release was a little hasty, and I missed a bunch of bugs. All of those should be squashed now.

#### Feb 18, 2006 ####
Version 0.6 released. Bug fixes.

#### Dec 16, 2005 ####
Version 0.5 released. Bug fixes and minor functionality added for SDP.

#### Nov 9, 2005 ####
Version 0.4 released. Minor bug fixes. No major new features.

#### Sep 20, 2005 ####
Version 0.3 released. Bug fixes for big-endian architectures, and sdp support. No major new features. Link added to some better documentation.

#### Apr 4, 2005 ####
Version 0.2 released. Support for SDP service advertisement and searching added. Support for easy asynchronous device discovery added. New API is incompatible with 0.1.

#### Dec 16, 2004 ####
Version 0.1 released. Support for HCI, L2CAP, and RFCOMM sockets.
No support for OBEX or SDP.