#!/usr/bin/env python
#coding:utf-8
# Purpose: algebra lib to calculate with geometric forms
# Created: 27.03.2010
# License: MIT License



import math

from .base import *
from .ray import Ray2D, ParallelRaysError
from .clothoid import Clothoid
from .circle import Circle
from .bezier import CubicBezierCurve
from .cspline import CubicSpline

__version__ = "v0.2 - 2010.03.27"
__author__ = "mozman <mozman@gmx.at>"
__license__ = "MIT License"

__doc__ = """A library to calculate with geometric forms.

Copyright %s
Version %s
License %s
""" % (__author__,__version__,__license__,)

# --------------------------------------------------------------------------
# algebra: copyright (C) 2010 by Manfred Moitzi (mozman)
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
