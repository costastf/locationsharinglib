#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: upload.py
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

import logging
import os

# this sets up everything and MUST be included before any third party module in every step
import _initialize_template

from emoji import emojize
from build import build
from library import execute_command, validate_environment_variable_prerequisites
from configuration import PREREQUISITES

# This is the main prefix used for logging
LOGGER_BASENAME = '''_CI.upload'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def upload():
    success = build()
    if not success:
        LOGGER.error('Errors caught on building the artifact, bailing out...')
        raise SystemExit(1)
    if not validate_environment_variable_prerequisites(PREREQUISITES.get('upload_environment_variables', [])):
        LOGGER.error('Prerequisite environment variable for upload missing, cannot continue.')
        raise SystemExit(1)
    upload_command = ('twine upload dist/* '
                      f'-u {os.environ.get("PYPI_UPLOAD_USERNAME")} '
                      f'-p {os.environ.get("PYPI_UPLOAD_PASSWORD")} '
                      '--skip-existing '
                      f'--repository-url {os.environ.get("PYPI_URL")}')
    LOGGER.info('Trying to upload built artifact...')
    success = execute_command(upload_command)
    if success:
        LOGGER.info('%s Successfully uploaded artifact! %s',
                    emojize(':white_heavy_check_mark:'),
                    emojize(':thumbs_up:'))
    else:
        LOGGER.error('%s Errors found in uploading artifact! %s',
                     emojize(':cross_mark:'),
                     emojize(':crying_face:'))
    raise SystemExit(0 if success else 1)


if __name__ == '__main__':
    upload()
