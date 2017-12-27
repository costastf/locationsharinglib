#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
from pipenv.project import Project
from collections import namedtuple

Package = namedtuple('Package', ['name', 'version'])

HEADER = """# 
# Please do not manually update this file since the requirements are managed
# by pipenv through Pipfile and Pipfile.lock . 
#
# This file is created and managed automatically by the template and it is left
# here only for backwards compatibility reasons with python's ecosystem.
#
# Please use Pipfile to update the requirements.
#
"""


def get_top_level_dependencies(package_type):
    validate_package_type(package_type)
    _type = 'packages' if package_type == 'default' else 'dev-packages'
    return Project().parsed_pipfile.get(_type, {}).keys()


def get_packages(package_type):
    validate_package_type(package_type)
    packages = json.loads(open('Pipfile.lock', 'r').read())
    return [Package(package_name, data.get('version'))
            for package_name, data in packages.get(package_type).items()]


def validate_package_type(package_type):
    if package_type not in ['default', 'develop']:
        raise ValueError('Invalid type received {}'.format(package_type))


if __name__ == '__main__':
    try:
        _type = sys.argv[1].lower()
    except IndexError:
        print('Please supply arguments, either "default" or "develop"')
        raise SystemExit(-1)
    top_level_dependencies = get_top_level_dependencies(_type)
    packages = get_packages(_type)
    packages = [package for package in packages
                if package.name in top_level_dependencies]
    ofile = 'requirements.txt' if _type == 'default' else 'dev-requirements.txt'
    with open(ofile, 'w') as f:
        f.write(HEADER + '\n'.join(['{}{}'.format(package.name, package.version)
                                    for package in packages]))

