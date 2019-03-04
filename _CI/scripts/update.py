#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: update.py
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
import tempfile
from glob import glob
from dataclasses import dataclass

# this sets up everything and MUST be included before any third party module in every step
import _initialize_template

from library import clean_up
from patch import fromfile, setdebug


@dataclass()
class Project:
    name: str
    full_path: str
    parent_directory_full_path: str


class PatchFailure(Exception):
    """The patch process failed"""


def get_current_version():
    with open(os.path.join('_CI', '.VERSION'), 'r') as version_file:
        version = version_file.read().strip()
        version_file.close()
    print(f'Got current template version {version}')
    return version


def apply_patch(file_path, project_parent_path):
    patcher = fromfile(file_path)
    return patcher.apply(0, project_parent_path)


def get_patches_to_apply(current_version):
    patches = []
    for patch_file in glob(os.path.join('_CI', 'patches', '*.patch')):
        version = patch_file.rpartition(os.path.sep)[2].split('.patch')[0]
        if version > current_version:
            patches.append(patch_file)
    return sorted(patches)


def get_interpolated_temp_patch_file(patch_file, project_name):
    patch_diff = open(patch_file, 'r').read()
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    temp_file.write(patch_diff.replace('{{cookiecutter.project_slug}}', project_name))
    temp_file.close()
    return temp_file.name


def initialize():
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_file_path, '..', '..'))
    project_parent_path, _, parent_directory_name = project_root.rpartition(os.path.sep)
    os.chdir(project_root)
    sys.path.append(os.path.join(project_root, '_CI/library'))
    setdebug()
    return Project(parent_directory_name, project_root, project_parent_path)


def apply_patches(patches, project):
    for diff_patch in patches:
        print(f'Interpolating project name "{project.name}" in patch {diff_patch}')
        patch_file = get_interpolated_temp_patch_file(diff_patch, project.name)
        success = apply_patch(patch_file, project.parent_directory_full_path)
        print(f'Removing temporary file "{patch_file}"')
        clean_up(patch_file)
        if success:
            print(f'Successfully applied patch {diff_patch}')
        else:
            print(f'Failed applying patch {diff_patch}')
            raise PatchFailure(diff_patch)


if __name__ == '__main__':
    project = initialize()
    current_version = get_current_version()
    patches_to_apply = get_patches_to_apply(current_version)
    try:
        apply_patches(patches_to_apply, project)
    except PatchFailure:
        SystemExit(1)
    raise SystemExit(0)
