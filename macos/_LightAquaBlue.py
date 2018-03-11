# Copyright (c) 2009 Bea Lam. All rights reserved.
#
# This file is part of LightBlue.
#
# LightBlue is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LightBlue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with LightBlue.  If not, see <http://www.gnu.org/licenses/>.

"""
Provides a python interface to the LightAquaBlue Framework classes, through
PyObjC.

See http://pyobjc.sourceforge.net for details on how to access Objective-C
classes through PyObjC.
"""

import objc
import os.path
from pkg_resources import resource_filename

_FRAMEWORK_PATH = resource_filename('lightblue', 'LightAquaBlue.framework')
if not os.path.isdir(_FRAMEWORK_PATH):
    raise ImportError("Cannot load LightAquaBlue framework, not found at " + \
        _FRAMEWORK_PATH)

__bundle__ = objc.initFrameworkWrapper("LightAquaBlue",
        frameworkIdentifier="com.blammit.LightAquaBlue",
        frameworkPath=objc.pathForFramework(_FRAMEWORK_PATH),
        globals=globals())

del objc
