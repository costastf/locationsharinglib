#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: rebuild_pipfile.py
#
# Copyright 2019 Ilija Matoski
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

import logging
import argparse

# this sets up everything and MUST be included before any third party module in every step
import _initialize_template

from bootstrap import bootstrap
from library import update_pipfile

# This is the main prefix used for logging
LOGGER_BASENAME = '''_CI.build'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())

def get_arguments():
    parser = argparse.ArgumentParser(description='Regenerates Pipfile based on Pipfile.lock')
    parser.add_argument('--stdout',
                        help='Output the Pipfile to stdout',
                        action="store_true",
                        default=False)
    args = parser.parse_args()
    return args


def execute():
    bootstrap()
    args = get_arguments()
    return update_pipfile(args.stdout)


if __name__ == '__main__':
    raise SystemExit(not execute())
