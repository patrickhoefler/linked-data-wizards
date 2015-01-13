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

"""Views relevant for the platform."""

from django.db.models import Count, Sum
from django.shortcuts import redirect
from django.views.generic import TemplateView
import urllib

from ldva.apps.platform.models import UserMeta
from ldva.libs.sparql.utils import SPARQLQuery
from ldva.libs.sparql.models import Dataset, Endpoint


class EndpointView(TemplateView):

    """View for the endpoint cube management page."""

    template_name = 'endpoints.html'

    def get_context_data(self, **kwargs):
        """Extend and return the context."""

        # Call the base implementation first to get a context
        context = super(EndpointView, self).get_context_data(**kwargs)

        # Add the list of endpoints and annotate with the dataset count
        context['endpoints'] = Endpoint.objects.annotate(
            dataset_count=Count('dataset')
        )

        return context


class StatsView(TemplateView):

    """View for the stats page."""

    template_name = 'stats.html'

    def get_context_data(self, **kwargs):
        """Extend and return the context."""

        # Call the base implementation first to get a context
        context = super(StatsView, self).get_context_data(**kwargs)

        # Add some endpoint statistics
        context['statistics'] = {
            'search_endpoints': Endpoint.objects.exclude(
                search_type='fuseki'
            ).aggregate(
                search_endpoint_count=Count('id')
            )['search_endpoint_count'],
            'cube_endpoints': Endpoint.objects.exclude(
                pk='code'
            ).annotate(
                dataset_count=Count('dataset')
            ).filter(
                dataset_count__gt=0
            ).aggregate(
                cube_endpoint_count=Count('id')
            )['cube_endpoint_count'],
            'datasets': Dataset.objects.aggregate(
                dataset_count=Count('uri')
            )['dataset_count'],
            'observations': Dataset.objects.aggregate(
                observations=Sum('size')
            )['observations'],
        }

        return context


class RobotsView(TemplateView):

    """
    Return robots.txt file

    """

    def get_template_names(self):
        return 'robots_allow.txt'


def incoming_from_qa_portal(request):
    """Make sure the user is logged in. Return an appropriate redirect."""

    # Make sure the user is logged in
    if not request.user.is_authenticated():
        # Redirect the user to Mendeley for authentication
        redirect_location = '/login/mendeley-oauth2/'
        redirect_location += '?next=/qa%3FuserId=' + urllib.quote_plus(request.GET.get('userId'))
        if request.GET.get('target'):
            redirect_location += '%26target=' + urllib.quote_plus(request.GET.get('target'))
        if request.GET.get('dataset'):
            redirect_location += '%26dataset=' + urllib.quote_plus(request.GET.get('dataset'))
        if request.GET.get('endpoint'):
            redirect_location += '%26endpoint=' + urllib.quote_plus(request.GET.get('endpoint'))
        if request.GET.get('callback'):
            redirect_location += '%26callback=' + urllib.quote_plus(request.GET.get('callback'))
        return redirect(redirect_location)
    else:
        # Save the 42-data ID to our UserMeta model
        if request.GET.get('userId'):
            user_meta = UserMeta(user=request.user, fortytwo_id=request.GET.get('userId'))
            user_meta.save()
        # Redirect the user
        if request.GET.get('target') == 'query' and request.GET.get('endpoint') and not request.GET.get('dataset'):
            return redirect('/search#?endpoint=' + urllib.quote_plus(request.GET.get('endpoint')))
        elif request.GET.get('target') == 'query' and request.GET.get('dataset') and request.GET.get('endpoint'):
            return redirect('/search#?dataset=' + urllib.quote_plus(request.GET.get('dataset')) + '&endpoint=' + urllib.quote_plus(request.GET.get('endpoint')) + '')
        elif request.GET.get('callback'):
            return redirect(request.GET.get('callback'))
        else:
            return redirect('/')


def reload_datasets(request, endpoint_url):
    """
    Reload the cube datasets of a SPARQL endpoint.

    Return a redirect to the same page.

    """
    endpoint = Endpoint.objects.get(pk=endpoint_url)
    sparql = SPARQLQuery(endpoint.sparql_url)

    sparql.refresh_dataset_list()

    return redirect('/endpoints')
