"""
Copyright (C) 2014 Kompetenzzentrum fuer wissensbasierte Anwendungen und Systeme
Forschungs- und Entwicklungs GmbH (Know-Center), Graz, Austria
office@know-center.at

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from social.backends.oauth import BaseOAuth1, BaseOAuth2


class MendeleyMixin(object):
    SCOPE_SEPARATOR = '+'
    EXTRA_DATA = [('profile_id', 'profile_id'),
                  ('name', 'name'),
                  ('bio', 'bio'),
                  ('full_name', 'full_name'),
                  ('photo_url', 'photo_url'),
                  ('profile_url', 'profile_url')]

    def get_user_id(self, details, response):
        return response['main']['profile_id']

    def get_user_details(self, response):
        """Return user details from Mendeley account"""
        # DEBUG: Display response from Mendeley
        # import pprint
        # pp = pprint.PrettyPrinter(indent=2)
        # pp.pprint(response)

        # Build the user details object
        details = {}

        name = ''
        if 'name' in response['main']:
            name = response['main']['name']
        details['full_name'] = name

        first_name = name
        last_name = ''
        if ' ' in name:
            split_name = name.split(' ')
            first_name = split_name[0]
            last_name = split_name[1]
        details['first_name'] = first_name
        details['last_name'] = last_name

        email = ''
        if 'email' in response['contact']:
            email = response['contact']['email']
        details['email'] = email

        photo_url = ''
        if 'photo' in response['main']:
            photo_url = response['main']['photo']
        details['photo_url'] = photo_url

        profile_url = ''
        if 'url' in response['main']:
            profile_url = response['main']['url']
        details['profile_url'] = profile_url

        return details

    def user_data(self, access_token, *args, **kwargs):
        """Return user data provided"""
        values = self.get_user_data(access_token)
        values.update(values['main'])
        return values

    def get_user_data(self, access_token):
        raise NotImplementedError('Implement in subclass')


class MendeleyOAuth(MendeleyMixin, BaseOAuth1):
    name = 'mendeley'
    AUTHORIZATION_URL = 'http://api.mendeley.com/oauth/authorize/'
    REQUEST_TOKEN_URL = 'http://api.mendeley.com/oauth/request_token/'
    ACCESS_TOKEN_URL = 'http://api.mendeley.com/oauth/access_token/'

    def get_user_data(self, access_token):
        return self.get_json(
            'http://api.mendeley.com/oapi/profiles/info/me/',
            auth=self.oauth_auth(access_token)
        )


class MendeleyOAuth2(MendeleyMixin, BaseOAuth2):
    name = 'mendeley-oauth2'
    AUTHORIZATION_URL = 'https://api-oauth2.mendeley.com/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://api-oauth2.mendeley.com/oauth/token'
    ACCESS_TOKEN_METHOD = 'POST'
    DEFAULT_SCOPE = ['all']
    REDIRECT_STATE = False
    EXTRA_DATA = MendeleyMixin.EXTRA_DATA + [
        ('refresh_token', 'refresh_token'),
        ('expires_in', 'expires_in'),
        ('token_type', 'token_type'),
    ]

    def get_user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        return self.get_json(
            'https://api-oauth2.mendeley.com/oapi/profiles/info/me/',
            headers={'Authorization': 'Bearer {0}'.format(access_token)}
        )
