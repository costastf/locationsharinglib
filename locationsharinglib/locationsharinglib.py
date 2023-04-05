#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: locationsharinglib.py
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
Main code for locationsharinglib.

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

from __future__ import unicode_literals

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import pytz
from cachetools import TTLCache, cached
from requests import Session

from .locationsharinglibexceptions import InvalidCookies, InvalidData, InvalidCookieFile

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''2017-12-24'''
__copyright__ = '''Copyright 2017, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos", "Michaël Arnauts", "Amy Nagle",
               "Jeremy Wiebe", "Chris Helming"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging
LOGGER_BASENAME = '''locationsharinglib'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())

STATE_CACHING_SECONDS = 30
STATE_CACHE = TTLCache(maxsize=1, ttl=STATE_CACHING_SECONDS)
VALID_COOKIE_NAMES = {'__Secure-1PSID', '__Secure-3PSID'}


@dataclass
class Cookie:
    """Models a cookie."""

    domain: str
    flag: bool
    path: str
    secure: bool
    expiry: int
    name: str
    value: str = ''
    rest: List = field(default_factory=list)

    def to_dict(self):
        """Returns the cookie as a dictionary.

        Returns:
            cookie (dict): The dictionary with the required values of the cookie

        """
        return {key: getattr(self, key) for key in ('domain', 'name', 'value', 'path')}


class Service:
    """An object modeling the service to retrieve locations."""

    def __init__(self, cookies_file=None, authenticating_account='unknown@gmail.com'):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self.email = authenticating_account
        self._session = self._validate_cookie(cookies_file or '')

    @staticmethod
    def _get_server_response(session):
        payload = {'authuser': 2,
                   'hl': 'en',
                   'gl': 'us',
                   # pd holds the information about the rendering of the map and
                   # it is irrelevant with the location sharing capabilities.
                   # the below info points to google's headquarters.
                   'pb': ('!1m7!8m6!1m3!1i14!2i8413!3i5385!2i6!3x4095'
                          '!2m3!1e0!2sm!3i407105169!3m7!2sen!5e1105!12m4'
                          '!1e68!2m2!1sset!2sRoadmap!4e1!5m4!1e4!8m2!1e0!'
                          '1e1!6m9!1e12!2i2!26m1!4b1!30m1!'
                          '1f1.3953487873077393!39b1!44e1!50e0!23i4111425')}
        url = 'https://www.google.com/maps/rpc/locationsharing/read'
        return session.get(url, params=payload, verify=True)

    @staticmethod
    def _parse_location_data(data):
        try:
            data = json.loads(data.split("'", 1)[1])
        except (ValueError, IndexError, TypeError):
            raise InvalidData(f'Received invalid data: {data}, cannot parse properly.') from None
        return data

    @staticmethod
    def _get_session_from_cookie_file(cookies_file_contents):
        try:
            session = Session()
            cookie_entries = [line.strip() for line in cookies_file_contents.splitlines()
                              if not line.strip().startswith('#') and line]
            cookies = []
            for entry in cookie_entries:
                domain, flag, path, secure, expiry, name, value, *rest = entry.split()
                cookies.append(Cookie(domain, flag, path, secure, expiry, name, value, rest))
            if not any(valid_name in {cookie.name for cookie in cookies} for valid_name in VALID_COOKIE_NAMES):
                raise InvalidCookies(f'Missing either of {VALID_COOKIE_NAMES} cookies!')
            for cookie in cookies:
                session.cookies.set(**cookie.to_dict())
        except TypeError:
            LOGGER.exception('Things broke...')
            raise InvalidCookieFile('Could not properly load cookie text file.') from None
        return session

    def _get_authenticated_session(self, cookies_file):
        try:
            with open(cookies_file, 'r', encoding='utf-8') as cfile:
                session = self._get_session_from_cookie_file(cfile.read())
        except FileNotFoundError:
            message = 'Could not open cookies file, either file does not exist or no read access.'
            raise InvalidCookieFile(message) from None
        return session

    def _validate_cookie(self, cookies_file):
        session = self._get_authenticated_session(cookies_file)
        data = self._parse_location_data(self._get_server_response(session).text)
        try:
            # it seems that if the 6th field of the data on the response is 'GgA=' then the session is not properly
            # authenticated so we use that heuristic for now which is less intrusive than reaching out to the personal
            # console of the user to check for a valid session.
            auth_field = data[6]
        except IndexError:
            raise InvalidData(f'Could not read 6th field of data, it seems invalid {data}') from None
        if auth_field == 'GgA=':
            raise InvalidCookies('Does not seem we have a valid session.')
        return session

    @cached(STATE_CACHE)
    def _get_data(self):
        response = self._get_server_response(self._session)
        self._logger.debug(f'Response status: {response.status_code}, body: {response.text}')
        if not response.ok:
            self._logger.warning(f'Received response code {response.status_code} with context {response.text}')
            return ['']
        return self._parse_location_data(response.text)

    def get_shared_people(self):
        """Retrieves all people that share their location with this account."""
        people = []
        output = self._get_data()
        self._logger.debug('Persons: %s', output)
        shared_entries = output[0] or []
        for info in shared_entries:
            try:
                people.append(Person(info))
            except InvalidData:
                self._logger.debug('Missing location or other info, dropping person with info: %s', info)
        return people

    def get_authenticated_person(self):
        """Retrieves the person associated with this account."""
        try:
            output = self._get_data()
            self._logger.debug('Creating person for authenticated account with email %s', self.email)
            person = Person([
                self.email,
                output[9][1],
                None,
                None,
                None,
                None,
                [
                    None,
                    None,
                    self.email,
                    self.email
                ],
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ])
        except (IndexError, TypeError, InvalidData) as err:
            self._logger.debug('Missing essential info, cannot instantiate authenticated person %s: %s', self.email,
                               str(err))
            return None
        return person

    def get_all_people(self):
        """Retrieves all people sharing their location."""
        people = self.get_shared_people() + [self.get_authenticated_person()]
        return filter(None, people)

    def get_person_by_nickname(self, nickname):
        """Retrieves a person by nickname."""
        return next((person for person in self.get_all_people()
                     if person.nickname.lower() == nickname.lower()), None)

    def get_coordinates_by_nickname(self, nickname):
        """Retrieves a person's coordinates by nickname."""
        person = self.get_person_by_nickname(nickname)
        if not person:
            return '', ''
        return person.latitude, person.longitude

    def get_latitude_by_nickname(self, nickname):
        """Retrieves a person's latitude by nickname."""
        person = self.get_person_by_nickname(nickname)
        if not person:
            return ''
        return person.latitude

    def get_longitude_by_nickname(self, nickname):
        """Retrieves a person's longitude by nickname."""
        person = self.get_person_by_nickname(nickname)
        if not person:
            return ''
        return person.longitude

    def get_timedate_by_nickname(self, nickname):
        """Retrieves a person's time in unix format by nickname."""
        person = self.get_person_by_nickname(nickname)
        if not person:
            return ''
        return person.timestamp

    def get_person_by_full_name(self, name):
        """Retrieves a person by full name."""
        return next((person for person in self.get_all_people()
                     if person.full_name.lower() == name.lower()), None)

    def get_coordinates_by_full_name(self, name):
        """Retrieves a person's coordinates by full name."""
        person = self.get_person_by_full_name(name)
        if not person:
            return '', ''
        return person.latitude, person.longitude

    def get_latitude_by_full_name(self, name):
        """Retrieves a person's latitude by name."""
        person = self.get_person_by_full_name(name)
        if not person:
            return ''
        return person.latitude

    def get_longitude_by_full_name(self, name):
        """Retrieves a person's longitude by name."""
        person = self.get_person_by_full_name(name)
        if not person:
            return ''
        return person.longitude

    def get_timedate_by_full_name(self, name):
        """Retrieves a person's time in unix format by name."""
        person = self.get_person_by_full_name(name)
        if not person:
            return ''
        return person.timestamp


class Person:
    """A person sharing its location as coordinates."""

    def __init__(self, data):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self._id = None
        self._picture_url = None
        self._full_name = None
        self._nickname = None
        self._latitude = None
        self._longitude = None
        self._timestamp = None
        self._accuracy = None
        self._address = None
        self._country_code = None
        self._charging = None
        self._battery_level = None
        self._populate(data)

    def _populate(self, data):
        try:
            self._id = data[6][0]
            self._picture_url = data[6][1]
            self._full_name = data[6][2]
            self._nickname = data[6][3]
            self._latitude = data[1][1][2]
            self._longitude = data[1][1][1]
            self._timestamp = data[1][2]
            self._accuracy = data[1][3]
            self._address = data[1][4]
            self._country_code = data[1][6]
            try:
                self._charging = data[13][0]
            except (IndexError, TypeError):
                self._charging = None
            try:
                self._battery_level = data[13][1]
            except (IndexError, TypeError):
                self._battery_level = None
        except (IndexError, TypeError):
            self._logger.debug(data)
            raise InvalidData from None

    def __str__(self):
        text = (f'Full name        :{self.full_name}',
                f'Nickname         :{self.nickname}',
                f'Current location :{self.address}',
                f'Latitude         :{self.latitude}',
                f'Longitude        :{self.longitude}',
                f'Datetime         :{self.datetime}',
                f'Charging         :{self.charging}',
                f'Battery %        :{self.battery_level}',
                f'Accuracy         :{self._accuracy}')
        return '\n'.join(text)

    @property
    def id(self):  # pylint: disable=invalid-name
        """The internal google id of the account."""
        return self._id or self.full_name

    @property
    def picture_url(self):
        """The url of the person's avatar."""
        return self._picture_url

    @property
    def full_name(self):
        """The full name of the user as set in google."""
        return self._full_name

    @property
    def nickname(self):
        """The nickname as set in google."""
        return self._nickname

    @property
    def latitude(self):
        """The latitude of the person's current location."""
        return self._latitude

    @property
    def longitude(self):
        """The longitude of the person's current location."""
        return self._longitude

    @property
    def timestamp(self):
        """The timestamp of the location retrieval."""
        return self._timestamp

    @property
    def datetime(self):
        """A datetime representation of the location retrieval."""
        return datetime.fromtimestamp(int(self.timestamp) / 1000, tz=pytz.utc)

    @property
    def address(self):
        """The address as reported by google for the current location."""
        return self._address

    @property
    def country_code(self):
        """The location's country code."""
        return self._country_code

    @property
    def accuracy(self):
        """The accuracy of the gps."""
        return self._accuracy

    @property
    def charging(self):
        """Whether or not the user's device is charging."""
        return bool(self._charging)

    @property
    def battery_level(self):
        """The battery level of the user's device."""
        return self._battery_level
