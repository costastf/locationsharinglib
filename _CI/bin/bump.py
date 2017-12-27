#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import argparse


import semver
import logging
LOGGER = logging.getLogger(__name__)


def get_arguments():
    """
    This get us the cli arguments.

    Returns the args as parsed from the argsparser.
    """
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(
        description='Handles bumping of the artifact version')
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
    parser.add_argument('--major',
                        help='Bump the major version',
                        dest='bump_major',
                        action='store_true',
                        default=False)
    parser.add_argument('--minor',
                        help='Bump the minor version',
                        dest='bump_minor',
                        action='store_true',
                        default=False)
    parser.add_argument('--patch',
                        help='Bump the patch version',
                        dest='bump_patch',
                        action='store_true',
                        default=False)
    parser.add_argument('--version',
                        help='Set the version',
                        dest='version',
                        action='store',
                        default=False)
    args = parser.parse_args()
    return args


def setup_logging(args):
    """
    This sets up the logging.

    Needs the args to get the log level supplied
    :param args: The command line arguments
    """
    handler = logging.StreamHandler()
    handler.setLevel(args.log_level)
    formatter = logging.Formatter(('%(asctime)s - '
                                   '%(name)s - '
                                   '%(levelname)s - '
                                   '%(message)s'))
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)


def main():
    """
    Main method.

    This method holds what you want to execute when
    the script is run on command line.
    """
    args = get_arguments()
    setup_logging(args)

    version_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        '.VERSION'
    ))

    try:
        version_text = open(version_path).read().strip()
    except Exception:
        print('Could not open or read the .VERSION file')
        sys.exit(1)

    try:
        semver.parse(version_text)
    except ValueError:
        print(('The .VERSION file contains an invalid '
               'version: "{}"').format(version_text))
        sys.exit(1)

    new_version = version_text
    if args.version:
        try:
            if semver.parse(args.version):
                new_version = args.version
        except Exception:
            print('Could not parse "{}" as a version'.format(args.version))
            sys.exit(1)
    elif args.bump_major:
        new_version = semver.bump_major(version_text)
    elif args.bump_minor:
        new_version = semver.bump_minor(version_text)
    elif args.bump_patch:
        new_version = semver.bump_patch(version_text)

    try:
        with open(version_path, 'w') as version_file:
            version_file.write(new_version)
    except Exception:
        print('Could not write the .VERSION file')
        sys.exit(1)
    print(new_version)


if __name__ == '__main__':
    main()
