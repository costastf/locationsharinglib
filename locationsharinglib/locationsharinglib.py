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
Main code for locationsharinglib

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

from __future__ import unicode_literals
import json
import logging
import pickle
from datetime import datetime

from bs4 import BeautifulSoup as Bfs
from cachetools import TTLCache, cached
from requests import Session

from .locationsharinglibexceptions import (InvalidCredentials,
                                           InvalidData,
                                           InvalidUser,
                                           InvalidCookies,
                                           TooManyFailedAuthenticationAttempts,
                                           NoExpectedFormOption,
                                           Unexpected2FAResponse)

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

INVALID_EMAIL_MESSAGE = 'Sorry, Google doesn&#39;t recognize that email.'
INVALID_PASSWORD_TOKEN = 'Wrong password. Try again.'  # noqa
TOO_MANY_ATTEMPTS = 'Unavailable because of too many failed attempts'
STATE_CACHING_SECONDS = 30

STATE_CACHE = TTLCache(maxsize=1, ttl=STATE_CACHING_SECONDS)


class Person:  # pylint: disable=too-many-instance-attributes
    """A person sharing its location as coordinates"""

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
            except TypeError:
                self._charging = None
            try:
                self._battery_level = data[13][1]
            except TypeError:
                self._battery_level = None
        except (IndexError, TypeError):
            self._logger.debug(data)
            raise InvalidData

    def __str__(self):
        text = (u'Full name        :{}'.format(self.full_name),
                u'Nickname         :{}'.format(self.nickname),
                u'Current location :{}'.format(self.address),
                u'Latitute         :{}'.format(self.latitude),
                u'Longitude        :{}'.format(self.longitude),
                u'Datetime         :{}'.format(self.datetime),
                u'Charging         :{}'.format(self.charging),
                u'Battery %        :{}'.format(self.battery_level),
                u'Accuracy         :{}'.format(self._accuracy))
        return '\n'.join(text)

    @property
    def id(self):  # pylint: disable=invalid-name
        """The internal google id of the account"""
        return self._id or self.full_name

    @property
    def picture_url(self):
        """The url of the person's avatar"""
        return self._picture_url

    @property
    def full_name(self):
        """The full name of the user as set in google"""
        return self._full_name

    @property
    def nickname(self):
        """The nickname as set in google"""
        return self._nickname

    @property
    def latitude(self):
        """The latitude of the person's current location"""
        return self._latitude

    @property
    def longitude(self):
        """The longitude of the person's current location"""
        return self._longitude

    @property
    def timestamp(self):
        """The timestamp of the location retrieval"""
        return self._timestamp

    @property
    def datetime(self):
        """A datetime representation of the location retrieval"""
        return datetime.fromtimestamp(int(self.timestamp) / 1000)

    @property
    def address(self):
        """The address as reported by google for the current location"""
        return self._address

    @property
    def country_code(self):
        """The location's country code"""
        return self._country_code

    @property
    def accuracy(self):
        """The accuracy of the gps"""
        return self._accuracy

    @property
    def charging(self):
        """Whether or not the user's device is charging"""
        return bool(self._charging)

    @property
    def battery_level(self):
        """The battery level of the user's device"""
        return self._battery_level


class Authenticator:  # pylint: disable=too-few-public-methods
    """Handles the authentication with google"""

    def __init__(self, email, password, cookies_file=None):
        logger_name = u'{base}.{suffix}'.format(base=LOGGER_BASENAME,
                                                suffix=self.__class__.__name__)
        self._logger = logging.getLogger(logger_name)
        self._session = Session()
        agent = ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) '
                 'Gecko/20100101 Firefox/59.0')
        self._session.headers.update({'User-Agent': agent,
                                      'Referer': 'https://www.google.com'})
        self.email = email
        self.password = password
        self._login_url = 'https://accounts.google.com'

        # Try login with cookie
        if cookies_file and self._validate_cookie(cookies_file):
            return

        # Try login based on username/password
        self._authenticate()
        if cookies_file:
            self._export_cookie(cookies_file)

    def _validate_cookie(self, cookies_file):
        try:
            cfile = open(cookies_file, 'rb')
            self._session.cookies = pickle.load(cfile)
        except KeyError:
            self._logger.error(('Could not load pickle file, '
                                'probably invalid pickle.'))
            return False
        except IOError:
            self._logger.error(('Could not open pickle file, either file '
                                'does not exist or no read access.'))
            return False

        # Check if cookies are valid
        response = self._session.get(self._login_url)
        if 'Sign in - Google Accounts' in response.text:
            message = ('The cookies provided do not provide a valid session.'
                       'Please authenticate normally and save a valid session '
                       'again')
            raise InvalidCookies(message)

        return True

    def _export_cookie(self, cookies_file):
        try:
            cfile = open(cookies_file, 'wb')
            pickle.dump(self._session.cookies, cfile)
        except IOError:
            message = 'Could not export cookies to {}.'.format(cookies_file)
            raise InvalidCookies(message)

    def _authenticate(self):
        initial_form = self._initialize()
        password_form = self._submit_email(initial_form)
        self._submit_password(password_form)

    def _initialize(self):
        url = '{login_url}/ServiceLogin'.format(login_url=self._login_url)
        response = self._session.get(url)
        soup = Bfs(response.text, 'html.parser')
        form = soup.find('form')
        return self._get_hidden_form_fields(form)

    def _submit_email(self, payload):
        url = '{login_url}/signin/v1/lookup'.format(login_url=self._login_url)
        payload['Email'] = self.email
        response = self._session.post(url, data=payload)
        if INVALID_EMAIL_MESSAGE in response.text:
            raise InvalidUser(self.email)
        soup = Bfs(response.text, 'html.parser')
        form = soup.find('form')
        return self._get_hidden_form_fields(form)

    def _submit_password(self, payload):
        url = ('{login_url}/signin/'
               'challenge/sl/password').format(login_url=self._login_url)
        payload['Passwd'] = self.password
        response = self._session.post(url, data=payload)
        if INVALID_PASSWORD_TOKEN in response.text:
            raise InvalidCredentials(response.text)
        elif TOO_MANY_ATTEMPTS in response.text:
            raise TooManyFailedAuthenticationAttempts(response.text)
        return response

    def _get_required_form(self, response, action):
        soup = Bfs(response.text, 'html.parser')
        form = next((form for form in soup.findAll('form')
                     if form.get('action', '') == action), None)
        if not form:
            self._logger.debug('Response : {}'.format(response.text))
            raise NoExpectedFormOption(response.text)
        return form

    def _submit_form(self, form):
        url = '{login_url}{action}'.format(login_url=self._login_url,
                                           action=form.get('action'))
        payload = self._get_hidden_form_fields(form)
        response = self._session.post(url, data=payload)
        return response

    def _skip_challenge(self, response):
        form = self._get_required_form(response, '/signin/challenge/skip')
        return self._submit_form(form)

    def _find_az(self, response):
        form = self._get_required_form(response, 'Tap Yes')
        if 'Too many' in form.text:
            raise TooManyFailedAuthenticationAttempts(response.text)
        return self._submit_form(form)

    def logout(self):
        """Logs the session out, invalidating the cookies

        Returns:
            True on success, False otherwise

        """
        url = '{login_url}/Logout'.format(login_url=self._login_url)
        response = self._session.get(url)
        return response.ok

    @staticmethod
    def _get_hidden_form_fields(form):
        return {field.get('name'): field.get('value')
                for field in form.find_all('input')}


class CookieGetter(Authenticator):  # pylint: disable=too-few-public-methods
    """Object to interactively get the cookies"""

    def __init__(self, email, password, cookies_file='authenticated.cookies'):
        super(CookieGetter, self).__init__(email,
                                           password,
                                           cookies_file=cookies_file)

    def _authenticate(self):
        initial_form = self._initialize()
        password_form = self._submit_email(initial_form)
        response = self._submit_password(password_form)
        if 'challenge/az' in response.url:
            self._handle_prompt(response)
        elif 'challenge/' in response.url:
            selection_form = self._skip_challenge(response)
            az_form = self._find_az(selection_form)
            self._handle_prompt(az_form)

    def _handle_prompt(self, response):
        # Borrowed with slight modification from https://git.io/vxu1A
        soup = Bfs(response.text, 'html.parser')
        challenge_url = response.url.split("?")[0]
        try:
            data_key = soup.find('div', {'data-api-key': True}).get('data-api-key')
            data_tx_id = soup.find('div', {'data-tx-id': True}).get('data-tx-id')
        except AttributeError:
            message = 'Unexpected response received :{}'.format(response.text)
            raise Unexpected2FAResponse(message)
        await_url = ('https://content.googleapis.com/cryptauth/v1/'
                     'authzen/awaittx?alt=json&key={}').format(data_key)
        await_body = {'txId': data_tx_id}

        print("Open the Google App, and tap 'Yes' on the prompt to sign in ...")

        self._session.headers['Referer'] = response.url
        response = self._session.post(await_url, json=await_body)
        parsed = json.loads(response.text)

        payload = {
            'challengeId': soup.find('input',
                                     {'name': 'challengeId'}).get('value'),
            'challengeType': soup.find('input',
                                       {'name': 'challengeType'}).get('value'),
            'TL': soup.find('input', {'name': 'TL'}).get('value'),
            'gxf': soup.find('input', {'name': 'gxf'}).get('value'),
            'token': parsed['txToken'],
            'action': soup.find('input', {'name': 'action'}).get('value'),
            'TrustDevice': 'on',
        }
        response = self._session.post(challenge_url, data=payload)
        response.raise_for_status()
        return response


class Service(Authenticator):
    """An object modeling the service to retrieve locations"""

    def __init__(self, email, password, cookies_file=None):
        super(Service, self).__init__(email,
                                      password,
                                      cookies_file=cookies_file)

    @cached(STATE_CACHE)
    def _get_data(self):
        payload = {'authuser': 0,
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
        url = 'https://www.google.com/maps/preview/locationsharing/read'
        response = self._session.get(url, params=payload)
        self._logger.debug(response.text)
        if response.ok:
            try:
                data = json.loads(response.text.split("'", 1)[1])
            except (ValueError, IndexError, TypeError):
                self._logger.exception('Unable to parse response :%s',
                                       response.text)
                data = ['']
        else:
            self._logger.warning('Received response code:%s', response.status_code)
            data = ['']
        return data

    def get_shared_people(self):
        """Retrieves all people that share their location with this account"""
        people = []
        output = self._get_data()
        for info in output[0]:
            try:
                people.append(Person(info))
            except InvalidData:
                self._logger.debug('Missing location or other info, dropping person with info: %s', info)
        return people

    def get_authenticated_person(self):
        """Retrieves the person associated with this account"""
        try:
            output = self._get_data()
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
        except (IndexError, TypeError, InvalidData):
            self._logger.debug('Missing essential info, cannot instantiate authenticated person')
            return None
        return person

    def get_all_people(self):
        """Retrieves all people sharing their location"""
        people = self.get_shared_people() + [self.get_authenticated_person()]
        return filter(None, people)

    def get_person_by_nickname(self, nickname):
        """Retrieves a person by nickname"""
        return next((person for person in self.get_all_people()
                     if person.nickname.lower() == nickname.lower()), None)

    def get_person_by_full_name(self, name):
        """Retrieves a person by full name"""
        return next((person for person in self.get_all_people()
                     if person.full_name.lower() == name.lower()), None)

    def get_coordinates_by_nickname(self, nickname):
        """Retrieves a person's coordinates by nickname"""
        person = self.get_person_by_nickname(nickname)
        if not person:
            return '', ''
        return person.latitude, person.longitude

    def get_coordinates_by_full_name(self, name):
        """Retrieves a person's coordinates by full name"""
        person = self.get_person_by_full_name(name)
        if not person:
            return '', ''
        return person.latitude, person.longitude
