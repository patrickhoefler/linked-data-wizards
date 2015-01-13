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

"""Definition of the URL mappings."""

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView
from ldva.apps.platform.views import EndpointView, StatsView, RobotsView
from ldva.apps.querywizard.views import SearchView
from ldva.apps.visbuilder.views import VisTestView, VisView, AutoView

admin.autodiscover()

urlpatterns = patterns(
    '',

    # Django Admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # CODE External Libraries
    url('', include('social.apps.django_app.urls', namespace='social')),

    # CODE Platform
    url(
        r'^logout$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name='auth_logout'
    ),
    (r'^stats$', StatsView.as_view()),
    (r'^endpoints$', EndpointView.as_view()),
    url(
        r'^endpoints/(.+)/datasets/reload$',
        'ldva.apps.platform.views.reload_datasets'
    ),
    url(r'^qa', 'ldva.apps.platform.views.incoming_from_qa_portal'),
    (r'^robots\.txt$', RobotsView.as_view()),

    # CODE Query Wizard
    (r'^$', RedirectView.as_view(url='/search', permanent=False)),
    (r'^search', SearchView.as_view()),
    url(
        r'^query/get_cube_dimensions_and_measures$',
        'ldva.apps.querywizard.views.get_cube_dimensions_and_measures'
    ),
    url(
        r'^query/get_subjects$',
        'ldva.apps.querywizard.views.get_subjects'
    ),
    url(
        r'^query/get_subjects_count$',
        'ldva.apps.querywizard.views.get_subjects_count'
    ),
    url(
        r'^query/get42data_datasets',
        'ldva.apps.querywizard.views.get42dataDatasets'
    ),
    url(
        r'^query/get_predicates_used_by_subjects$',
        'ldva.apps.querywizard.views.get_predicates_used_by_subjects'
    ),
    url(
        r'^query/get_objects_for_predicate$',
        'ldva.apps.querywizard.views.get_objects_for_predicate'
    ),
    url(
        r'^query/get_datasets$',
        'ldva.apps.querywizard.views.get_datasets'
    ),
    url(
        r'^query/get_dataset_label$',
        'ldva.apps.querywizard.views.get_dataset_label'
    ),
    url(
        r'^query/get_comprehensive_sparql_query$',
        'ldva.apps.querywizard.views.get_comprehensive_sparql_query'
    ),
    url(
        r'^query/save_data',
        'ldva.apps.querywizard.views.save_data'
    ),
    url(
        r'^query/save_query',
        'ldva.apps.querywizard.views.save_query'
    ),
    url(
        r'^query/save_visualization',
        'ldva.apps.querywizard.views.save_visualization'
    ),
    url(
        r'^query/aggregate$',
        'ldva.apps.querywizard.views.aggregate'
    ),

    # CODE Vis Builder
    (r'^vistest', VisTestView.as_view()),
    url(r'^visimage', 'ldva.libs.phantomjs.phantom.vismage_capture'),
    url(r'^phantom', 'ldva.libs.phantomjs.phantom.phantom_capture'),
    (r'^vis', VisView.as_view()),
    (r'^autotest', AutoView.as_view()),

    url(r'^viz', 'ldva.apps.visbuilder.codeviz.service', name='service'),

    # Cubifier Test
    url(
        r'^cubifier',
        'ldva.libs.cubifier.views.test'
    ),

)
