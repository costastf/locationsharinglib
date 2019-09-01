#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: reset.py
#
# Copyright 2018 Costas Tyfoxylos
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

import os
import sys
import shutil
import stat
import logging

# this sets up everything and MUST be included before any third party module in every step
import _initialize_template

from configuration import ENVIRONMENT_VARIABLES
from library import clean_up, get_project_root_path

# This is the main prefix used for logging
LOGGER_BASENAME = '''_CI.reset'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def reset(environment_variables):
    pipfile_path = environment_variables.get('PIPENV_PIPFILE', 'Pipfile')
    venv = os.path.join(get_project_root_path(), os.path.dirname(pipfile_path), '.venv')
    clean_up(venv)


if __name__ == '__main__':
    reset(ENVIRONMENT_VARIABLES)
