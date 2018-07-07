#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: locationsharinglibexceptions.py
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
Custom exception code for locationsharinglib

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''2017-12-24'''
__copyright__ = '''Copyright 2017, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos", "Chris Helming"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


class InvalidData(Exception):
    """The data received do not fit the expected format"""


class InvalidCredentials(Exception):
    """The provided credentials were not accepted"""


class InvalidUser(Exception):
    """The email or phone is not recognised as belonging to a valid user"""


class InvalidCookies(Exception):
    """The cookies provided do not provide a valid session"""


class TooManyFailedAuthenticationAttempts(Exception):
    """The authentication attempt quota has been reached"""


class NoExpectedFormOption(Exception):
    """There was no form presented with the expected option"""


class Unexpected2FAResponse(Exception):
    """The response received was not expected"""
