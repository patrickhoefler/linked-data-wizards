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

from django.utils import simplejson
from social_auth.backends import ConsumerBasedOAuth, OAuthBackend


MENDELEY_REQUEST_TOKEN_URL = 'http://www.mendeley.com/oauth/request_token/'
MENDELEY_ACCESS_TOKEN_URL = 'http://www.mendeley.com/oauth/access_token/'
MENDELEY_AUTHORIZATION_URL = 'http://www.mendeley.com/oauth/authorize/'
MENDELEY_CHECK_AUTH = 'http://api.mendeley.com/oapi/profiles/info/me/'


class MendeleyBackend(OAuthBackend):
    """Mendeley OAuth authentication backend"""
    name = 'mendeley'

    def get_user_id(self, details, response):
        return response['main']['profile_id']

    def extra_data(self, user, uid, response, details):
        """
        Return user extra data
        """
        data = super(MendeleyBackend, self).extra_data(user, uid, response, details)
        data['full_name'] = details['full_name']
        data['photo_url'] = details['photo_url']
        data['profile_url'] = details['profile_url']
        return data

    def get_user_details(self, response):
        """
        Return the user details
        """
        # DEBUG: Display response from Mendeley
        #import pprint
        #pp = pprint.PrettyPrinter(indent=2)
        #pp.pprint(response)

        # Build the user details object
        details = {}

        name = ''
        if 'name' in response['main']:
            name = response['main']['name']
        details['username'] = name
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


class MendeleyAuth(ConsumerBasedOAuth):
    """Mendeley OAuth authentication mechanism"""
    AUTHORIZATION_URL = MENDELEY_AUTHORIZATION_URL
    REQUEST_TOKEN_URL = MENDELEY_REQUEST_TOKEN_URL
    ACCESS_TOKEN_URL = MENDELEY_ACCESS_TOKEN_URL
    SERVER_URL = "api.mendeley.com"
    AUTH_BACKEND = MendeleyBackend
    SETTINGS_KEY_NAME = 'MENDELEY_CONSUMER_KEY'
    SETTINGS_SECRET_NAME = 'MENDELEY_CONSUMER_SECRET'

    def user_data(self, access_token):
        """Return user data provided"""
        url = MENDELEY_CHECK_AUTH
        request = self.oauth_request(access_token, url)
        raw_json = self.fetch_response(request)
        try:
            return simplejson.loads(raw_json)
        except:
            return None

    @classmethod
    def enabled(cls):
        return True


BACKENDS = {
    'mendeley': MendeleyAuth,
}
