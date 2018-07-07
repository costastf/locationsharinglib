#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: __init__.py
#
# Copyright 2017 Costas Tyfoxylos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
locationsharinglib package

Import all parts from locationsharinglib here

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html
"""
from ._version import __version__
from .locationsharinglibexceptions import (InvalidData,
                                           InvalidCredentials,
                                           InvalidCookies,
                                           TooManyFailedAuthenticationAttempts,
                                           NoExpectedFormOption,
                                           Unexpected2FAResponse)
from .locationsharinglib import Service, Person, CookieGetter

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''2017-12-24'''
__copyright__ = '''Copyright 2017, Costas Tyfoxylos'''
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is to 'use' the module(s), so lint doesn't complain
assert __version__

# assert objects
assert Service
assert Person
assert CookieGetter

# assert exceptions
assert InvalidData
assert InvalidCredentials
assert InvalidCookies
assert TooManyFailedAuthenticationAttempts
assert NoExpectedFormOption
assert Unexpected2FAResponse
