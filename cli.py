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

import logging
import logging.config
import json
import argparse

from locationsharinglib import CookieGetter
from locationsharinglib import Unexpected2FAResponse

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''2017-12-24'''
__copyright__ = '''Copyright 2017, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging
LOGGER_BASENAME = '''GetMapsCookies'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def get_arguments():
    """
    Gets us the cli arguments.

    Returns the args as parsed from the argsparser.
    """
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description=('A tool to interactively '
                                                  'handle authentication for '
                                                  'google maps and 2FA'))
    parser.add_argument('--log-config',
                        '-l',
                        action='store',
                        dest='logger_config',
                        help='The location of the logging config json file',
                        default='')
    parser.add_argument('--log-level',
                        '-L',
                        help='Provide the log level. Defaults to INFO.',
                        dest='log_level',
                        action='store',
                        default='INFO',
                        choices=['DEBUG',
                                 'INFO',
                                 'WARNING',
                                 'ERROR',
                                 'CRITICAL'])
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


def setup_logging(args):
    """Sets up the logging.

    Needs the args to get the log level supplied
    Args:
        args: The arguments returned gathered from argparse
    """
    # This will configure the logging, if the user has set a config file.
    # If there's no config file, logging will default to stdout.
    if args.logger_config:
        # Get the config for the logger. Of course this needs exception
        # catching in case the file is not there and everything. Proper IO
        # handling is not shown here.
        configuration = json.loads(open(args.logger_config).read())
        # Configure the logger
        logging.config.dictConfig(configuration)
    else:
        handler = logging.StreamHandler()
        handler.setLevel(args.log_level)
        formatter = logging.Formatter(('%(asctime)s - '
                                       '%(name)s - '
                                       '%(levelname)s - '
                                       '%(message)s'))
        handler.setFormatter(formatter)
        LOGGER.addHandler(handler)
        LOGGER.setLevel(args.log_level.upper())


def main():
    """Interactively handles the authentication"""
    args = get_arguments()
    setup_logging(args)
    try:
        CookieGetter(args.email, args.password, args.cookies_file)
    except Unexpected2FAResponse as exc:
        raise SystemExit(exc)


if __name__ == '__main__':
    main()
