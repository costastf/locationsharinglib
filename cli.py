#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: cli.py
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
Main code for locationsharinglib

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import argparse

from locationsharinglib import CookieGetter

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''2017-12-24'''
__copyright__ = '''Copyright 2017, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


def get_arguments():
    """
    Gets us the cli arguments.

    Returns the args as parsed from the argsparser.
    """
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description=('A tool to interactively '
                                                  'handle authentication for '
                                                  'google maps and 2FA'))
    parser.add_argument('--email', '-e',
                        dest='email',
                        action='store',
                        help='The email of the account to authenticate',
                        required=True)
    parser.add_argument('--password', '-p',
                        dest='password',
                        action='store',
                        help='The password of the account to authenticate',
                        required=True)
    parser.add_argument('--cookies-file', '-c',
                        dest='cookies_file',
                        action='store',
                        help='The file to output the cookies to',
                        default='.google_maps_location_sharing.cookies')
    args = parser.parse_args()
    return args


def main():
    """Interactively handles the authentication"""
    args = get_arguments()
    CookieGetter(args.email, args.password, args.cookies_file)


if __name__ == '__main__':
    main()
