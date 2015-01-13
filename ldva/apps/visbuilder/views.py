# encoding: utf-8
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

from __future__ import unicode_literals

from django.conf import settings
from django.views.generic import TemplateView
from datetime import datetime
from ldva.apps.platform.models import UserMeta
from ldva.libs.sparql.models import Endpoint
from django.db.models import Count


class VisTestView(TemplateView):
    template_name = "vistest.html"


class VisView(TemplateView):
    template_name = "vis.html"
    def get_context_data(self, **kwargs):
        context = super(VisView, self).get_context_data(**kwargs)
        context['time'] = datetime.now()

        # Check if "Log in with Mendeley" is enabled
        context['mendeley_login_enabled'] = False
        if settings.SOCIAL_AUTH_MENDELEY_OAUTH2_KEY != '':
            context['mendeley_login_enabled'] = True

        # If a user is logged in, get the social auth extra data
        context['mendeley_id'] = ''
        context['mendeley_full_name'] = ''
        context['mendeley_profile_url'] = ''
        context['mendeley_photo_url'] = ''
        if self.request.user.is_authenticated():
            # FIXME: When using more than one oAuth providers, the next line might get the wrong one
            social_user = self.request.user.social_auth.all()[0]
            context['mendeley_id'] = social_user.uid
            if 'full_name' in social_user.extra_data:
                context['mendeley_full_name'] = social_user.extra_data['full_name']
            if 'profile_url' in social_user.extra_data:
                context['mendeley_profile_url'] = social_user.extra_data['profile_url']
            if 'photo_url' in social_user.extra_data:
                context['mendeley_photo_url'] = social_user.extra_data['photo_url']

            # Get the 42-data ID for the logged-in user, if there is one
            try:
                user_meta = UserMeta.objects.get(pk=self.request.user)
                context['fortytwo_id'] = user_meta.fortytwo_id
            except UserMeta.DoesNotExist:
                context['fortytwo_id'] = ''

        # Add all endpoints that provide datasets (except code and marvin)
        context['cube_endpoints'] = Endpoint.objects.exclude(
            pk='code'
        ).exclude(
            pk='marvin'
        ).annotate(
            dataset_count=Count('dataset')
        ).filter(
            dataset_count__gt=0
        )

        return context

class AutoView(TemplateView):
    template_name = "autotest.html"
