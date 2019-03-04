#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: tag.py
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

import argparse
import logging

from datetime import datetime

# this sets up everything and MUST be included before any third party module in every step
import _initialize_template

from emoji import emojize
from bootstrap import bootstrap
from gitwrapperlib import Git
from library import bump
from configuration import BRANCHES_SUPPORTED_FOR_TAG


# This is the main prefix used for logging
LOGGER_BASENAME = '''_CI.tag'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def check_branch():
    git = Git()
    if git.get_current_branch() not in BRANCHES_SUPPORTED_FOR_TAG:
        accepted_branches = ', '.join(BRANCHES_SUPPORTED_FOR_TAG)
        print("Tagging is only supported on {} "
              "you should not tag any other branch, exiting!".format(accepted_branches))
        raise SystemExit(1)


def push(current_version):
    git = Git()
    git.commit('Updated history file with changelog', 'HISTORY.rst')
    git.commit('Set version to {}'.format(current_version), '.VERSION')
    git.add_tag(current_version)
    git.push()
    git.push('origin', current_version)
    return current_version


def _get_user_input(version):
    print(f'Enter/Paste your history changelog for version {version}.\n'
          f'Each comment can be a different line.\n\n'
          f'Ctrl-D ( Mac | Linux ) or Ctrl-Z ( windows ) to save it.\n')
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)
    return contents


def _get_changelog(contents, version):
    header = f'{version} ({datetime.today().strftime("%d-%m-%Y")})'
    underline = '-' * len(header)
    return (f'\n\n{header}\n'
            f'{underline}\n\n* ' + '\n* '.join([line for line in contents if line]) + '\n')


def update_history_file(version):
    comments = _get_user_input(version)
    update_text = _get_changelog(comments, version)
    with open('HISTORY.rst', 'a') as history_file:
        history_file.write(update_text)
        history_file.close()


def get_arguments():
    parser = argparse.ArgumentParser(description='Handles bumping of the artifact version')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--major', help='Bump the major version', action='store_true')
    group.add_argument('--minor', help='Bump the minor version', action='store_true')
    group.add_argument('--patch', help='Bump the patch version', action='store_true')
    args = parser.parse_args()
    return args


def tag():
    bootstrap()
    args = get_arguments()
    check_branch()
    if args.major:
        version = bump('major')
        update_history_file(version)
    elif args.minor:
        version = bump('minor')
        update_history_file(version)
    elif args.patch:
        version = bump('patch')
        update_history_file(version)
    else:
        version = bump()
        print(version)
        raise SystemExit(0)
    version = push(version)
    print(version)


if __name__ == '__main__':
    tag()
