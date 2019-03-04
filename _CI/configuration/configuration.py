#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: configuration.py
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
import json

current_file_path = os.path.dirname(os.path.abspath(__file__))
files_path = os.path.abspath(os.path.join(current_file_path, '..', 'files'))

with open(os.path.join(files_path, 'logging_level.json'), 'r') as logging_level_file:
    LOGGING_LEVEL = json.loads(logging_level_file.read()).get('level').upper()
    logging_level_file.close()

with open(os.path.join(files_path, 'environment_variables.json'), 'r') as environment_variables_file:
    ENVIRONMENT_VARIABLES = json.loads(environment_variables_file.read())
    environment_variables_file.close()

with open(os.path.join(files_path, 'prerequisites.json'), 'r') as prerequisites_file:
    PREREQUISITES = json.loads(prerequisites_file.read())
    prerequisites_file.close()

BUILD_REQUIRED_FILES = ('.VERSION',
                        'LICENSE',
                        'AUTHORS.rst',
                        'CONTRIBUTING.rst',
                        'HISTORY.rst',
                        'README.rst',
                        'USAGE.rst',
                        'Pipfile',
                        'Pipfile.lock',
                        'requirements.txt',
                        'dev-requirements.txt')

LOGGERS_TO_DISABLE = ['sh.command',
                      'sh.command.process',
                      'sh.command.process.streamreader',
                      'sh.streamreader',
                      'sh.stream_bufferer']

BRANCHES_SUPPORTED_FOR_TAG = ['master']

PROJECT_SLUG = ENVIRONMENT_VARIABLES.get('PROJECT_SLUG')
