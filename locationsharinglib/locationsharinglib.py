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
   http://google.github.io/styleguide/pyguide.html

"""

from __future__ import unicode_literals

import json
import logging
import pickle
import warnings
from dataclasses import dataclass
from datetime import datetime

import pytz
from cachetools import TTLCache, cached
from requests import Session

from .locationsharinglibexceptions import InvalidCookies, InvalidData

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
ACCOUNT_URL = 'https://myaccount.google.com/?hl=en'


@dataclass
class Cookie:
    """Models a cookie."""

    domain: str
    flag: bool
    path: str
    secure: bool
    expiry: int
    name: str
    value: str

    def to_dict(self):
        """Returns the cookie as a dictionary.

        Returns:
            cookie (dict): The dictionary with the required values of the cookie

        """
        return {key: getattr(self, key) for key in ('domain', 'name', 'value', 'path')}


class Service:
    """An object modeling the service to retrieve locations."""

    def __init__(self, cookies_file=None, authenticating_account='unknown@gmail.com'):
        logger_name = u'{base}.{suffix}'.format(base=LOGGER_BASENAME,
                                                suffix=self.__class__.__name__)
        self._logger = logging.getLogger(logger_name)
        self.email = authenticating_account
        self._session = self._validate_cookie(cookies_file or '')

    def _validate_cookie(self, cookies_file):
        session = self._get_authenticated_session(cookies_file)
        response = session.get(ACCOUNT_URL)
        self._logger.debug('Getting personal account page and its cookies...\n %s', response.content)
        response = session.get(ACCOUNT_URL)
        self._logger.debug('Validating access to personal account...')
        if response.history:
            message = ('The cookies provided do not provide a valid session, could not reach personal account page.'
                       'Please create another cookie file and try again.')
            raise InvalidCookies(message)
        return session

    def _get_authenticated_session(self, cookies_file):
        session = Session()
        try:
            cfile = open(cookies_file, 'rb')
        except FileNotFoundError:
            message = 'Could not open cookies file, either file does not exist or no read access.'
            raise InvalidCookies(message)
        try:
            session.cookies.update(pickle.load(cfile))
            self._logger.debug('Successfully loaded pickled cookie!')
            warnings.warn('Pickled cookie format is going to be deprecated in a future version, '
                          'please start using a text base cookie file!')
        except (pickle.UnpicklingError, KeyError, AttributeError, EOFError, ValueError):
            self._logger.debug('Trying to load text based cookies.')
            session = self._load_text_cookies(session, cfile)
        cfile.close()
        return session

    def _load_text_cookies(self, session, cookies_file):
        try:
            text = cookies_file.read().decode('utf-8')
            cookies = [Cookie(*line.strip().split()) for line in text.splitlines()
                       if not line.strip().startswith('#') and line]
            for cookie in cookies:
                session.cookies.set(**cookie.to_dict())
        except Exception:
            self._logger.exception('Things broke...')
            message = 'Could not properly load cookie text file.'
            raise InvalidCookies(message)
        return session

    @cached(STATE_CACHE)
    def _get_data(self):
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
        response = self._session.get(url, params=payload, verify=True)
        self._logger.debug('Response status: %s, body: %s', response.reason, repr(response.text))
        if response.ok:
            try:
                data = json.loads(response.text.split("'", 1)[1])
            except (ValueError, IndexError, TypeError):
                self._logger.exception('Unable to parse response from %s: %s',
                                       url, response.text)
                data = ['']
        else:
            self._logger.warning('Received response code %s from %s', response.status_code, url)
            data = ['']
        return data

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

    def get_person_by_full_name(self, name):
        """Retrieves a person by full name."""
        return next((person for person in self.get_all_people()
                     if person.full_name.lower() == name.lower()), None)

    def get_coordinates_by_nickname(self, nickname):
        """Retrieves a person's coordinates by nickname."""
        person = self.get_person_by_nickname(nickname)
        if not person:
            return '', ''
        return person.latitude, person.longitude

    def get_coordinates_by_full_name(self, name):
        """Retrieves a person's coordinates by full name."""
        person = self.get_person_by_full_name(name)
        if not person:
            return '', ''
        return person.latitude, person.longitude


class Person:  # pylint: disable=too-many-instance-attributes
    """A person sharing its location as coordinates."""

    def __init__(self, data):
        logger_name = u'{base}.{suffix}'.format(base=LOGGER_BASENAME,
                                                suffix=self.__class__.__name__)
        self._logger = logging.getLogger(logger_name)
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
            raise InvalidData

    def __str__(self):
        text = (u'Full name        :{}'.format(self.full_name),
                u'Nickname         :{}'.format(self.nickname),
                u'Current location :{}'.format(self.address),
                u'Latitude         :{}'.format(self.latitude),
                u'Longitude        :{}'.format(self.longitude),
                u'Datetime         :{}'.format(self.datetime),
                u'Charging         :{}'.format(self.charging),
                u'Battery %        :{}'.format(self.battery_level),
                u'Accuracy         :{}'.format(self._accuracy))
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
