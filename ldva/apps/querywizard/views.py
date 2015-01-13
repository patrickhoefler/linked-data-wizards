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

"""Views for the Query Wizard."""

import cgi
from django.conf import settings
from django.db.models import Count
from django.db.models.base import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import simplejson
from django.views.generic import TemplateView
import re
import requests
from string import Template
import urllib


from ldva.apps.platform.models import UserMeta
from ldva.libs.sparql.models import Dataset, Endpoint
from ldva.libs.sparql.utils import SPARQLQuery, shorten_uri
from ldva.libs.cubifier import cubegen


class SearchView(TemplateView):

    """Default view for the Query Wizard."""

    template_name = 'querywizard.html'

    def get_context_data(self, **kwargs):
        """Extend and return the context."""
        # Call the base implementation first to get a context
        context = super(SearchView, self).get_context_data(**kwargs)

        # Check if "Log in with Mendeley" is enabled
        context['mendeley_login_enabled'] = False
        if settings.SOCIAL_AUTH_MENDELEY_OAUTH2_KEY != '':
            context['mendeley_login_enabled'] = True

        # Add all searchable endpoints
        context['search_endpoints'] = Endpoint.objects.exclude(
            search_type='fuseki'
        )

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

        # If a user is logged in, get the social auth extra data
        context['mendeley_id'] = ''
        context['mendeley_full_name'] = ''
        context['mendeley_profile_url'] = ''
        context['mendeley_photo_url'] = ''
        if self.request.user.is_authenticated():
            # The following doesn't work if using multiple oAuth providers
            social_user = self.request.user.social_auth.all()[0]
            context['mendeley_id'] = social_user.uid
            if 'full_name' in social_user.extra_data:
                context['mendeley_full_name'] = \
                    social_user.extra_data['full_name']
            if 'profile_url' in social_user.extra_data:
                context['mendeley_profile_url'] = \
                    social_user.extra_data['profile_url']
            if 'photo_url' in social_user.extra_data:
                context['mendeley_photo_url'] = \
                    social_user.extra_data['photo_url']

            # Get the 42-data ID for the logged-in user, if there is one
            try:
                user_meta = UserMeta.objects.get(pk=self.request.user)
                context['fortytwo_id'] = user_meta.fortytwo_id
            except UserMeta.DoesNotExist:
                context['fortytwo_id'] = ''

        return context


@csrf_exempt
def get_subjects(request):
    """
    Get the RDF subjects that match the current filters.

    Return a dictionary with the subject list.

    """
    data = simplejson.loads(request.body)
    sparql = SPARQLQuery(data['endpoint_url'], data['search_type'])

    subjects_raw = sparql.get_subjects(
        data['predicates'],
        data['offset'],
        data['dataset'],
    )

    subjects = []
    for subject in subjects_raw['subjects']:
        subjects.append(subject)

    return HttpResponse(
        simplejson.dumps({
            'subjects': subjects,
            'runtime': subjects_raw['time'],
            'query': subjects_raw['query'],
            'endpoint_url': subjects_raw['endpoint_url'],
        }),
        mimetype='application/json'
    )


@csrf_exempt
def get42dataDatasets(request):
    """
    """
    data = simplejson.loads(request.body)
    sparql = SPARQLQuery(data['endpoint_url'], "virtuoso")

    query = Template("""
    SELECT ?dataset ?label WHERE {
      ?dataset <http://www.w3.org/ns/prov#wasGeneratedBy> ?generated_by .
      ?dataset <http://www.w3.org/2000/01/rdf-schema#label> ?label .
      ?generated_by <http://www.w3.org/ns/prov#wasStartedBy> ?started_by .
      ?started_by <http://www.w3.org/2000/01/rdf-schema#label> ?user
      FILTER (?user = "$userId"^^<http://www.w3.org/2001/XMLSchema#string>) .
    }""").substitute({
                'userId': data['userId']
            })

    queryResult = sparql.query(query)

    response = {}

    # Add info for the selected endpoint
    selected_endpoint = Endpoint.objects.get(
        sparql_url=data['endpoint_url']
    )
    response['endpoint'] = Endpoint.objects.filter(
        sparql_url=data['endpoint_url']
    ).values(
        'label', 'website_url'
    )[0]

    response['datasets'] = []
    for result in queryResult["results"]["bindings"]:
        responseRow = {}
        responseRow["uri"] = result["dataset"]["value"]
        responseRow["label"] = result["label"]["value"]
        responseRow["size"] = 0
        response['datasets'].append(responseRow)

    return HttpResponse(
        simplejson.dumps(response),
        mimetype='application/json'
    )


@csrf_exempt
def get_subjects_count(request):
    """
    Get the count of the RDF subjects that match the current filters.

    Return a dictionary with the subjects count.

    """
    data = simplejson.loads(request.body)
    sparql = SPARQLQuery(data['endpoint_url'], data['search_type'])

    subjects_count_raw = sparql.get_subjects_count(
        data['predicates'],
        data['dataset'],
    )

    return HttpResponse(
        simplejson.dumps({
            'subjects_count': subjects_count_raw['count'],
            'runtime': subjects_count_raw['time'],
            'query': subjects_count_raw['query'],
        }),
        mimetype='application/json'
    )


@csrf_exempt
def get_predicates_used_by_subjects(request):
    """
    Get the RDF predicates used by the given subjects.

    Return a dictionary with the predicates and their respective label.

    """
    data = simplejson.loads(request.body)
    sparql = SPARQLQuery(data['endpoint_url'], data['search_type'])

    predicates_raw = sparql.get_predicates(
        data['subjects'],
    )

    predicates = []
    for predicate in predicates_raw['predicates']:
        predicates.append({
            'uri': predicate['uri'],
            'label': predicate['label'],
            'inverse': predicate['inverse'],
        })

    return HttpResponse(
        simplejson.dumps({
            'predicates': predicates,
            'runtime': predicates_raw['time'],
            'query': predicates_raw['query'],
        }),
        mimetype='application/json',
    )


@csrf_exempt
def get_objects_for_predicate(request):
    """
    Get the objects for the given subjects and predicate.

    Return a dictionary with the predicate and the found objects.

    """
    data = simplejson.loads(request.body)
    sparql = SPARQLQuery(data['endpoint_url'], data['search_type'])

    objects_raw = sparql.get_objects(
        data['subjects'],
        data['predicate'],
    )

    objects = []
    for row in objects_raw['table']:
        sub = row['s']
        obj = row['o']['value']
        if row['o']['type'] == 'uri':
            temp_object = {
                's': sub,
                'o': {
                    'type': row['o']['type'],
                    'uri': obj
                }
            }
            if 'label' in row['o']:
                temp_object['o']['label'] = row['o']['label']['value']
            objects.append(temp_object)
        else:
            temp_object = {
                's': sub,
                'o': {
                    'type': row['o']['type'],
                    'label': obj,
                }
            }
            if row['o'].get('datatype'):
                temp_object['o']['datatype'] = row['o'].get('datatype')
            objects.append(temp_object)

    return HttpResponse(
        simplejson.dumps({
            'predicate': data['predicate'],
            'objects': objects,
            'runtime': objects_raw['time'],
            'query': objects_raw['query'],
        }),
        mimetype='application/json'
    )


@csrf_exempt
def get_comprehensive_sparql_query(request):
    """
    Get the SPARQL query that rules them all.

    Return JSON containing the query.

    """
    data = simplejson.loads(request.body)
    sparql = SPARQLQuery(data['endpoint_url'], data['search_type'])

    query = sparql.get_comprehensive_sparql_query(
        data['predicates'],
        data['dataset'],
    )

    return HttpResponse(
        simplejson.dumps({
            'query': query,
        }),
        mimetype='application/json'
    )


@csrf_exempt
def get_cube_dimensions_and_measures(request):
    """
    Get the dimensions and measures of the currently displayed cube.

    Return a list of the cube dimension dictionaries containing uri and label
    as well as a list of the cube measure dictionaries containing the uri.

    """
    data = simplejson.loads(request.body)
    sparql = SPARQLQuery(data['endpoint_url'], data['search_type'])

    output = {}

    # Get the dimensions
    dimensions_raw = sparql.get_cube_dimensions(data['dataset'])

    dimensions = []
    for dimension in dimensions_raw:
        dimensions.append(
            {
                'uri': dimension['dimensionuri'],
                'label': dimension['label'],
            }
        )

    output['dimensions'] = dimensions

    # Get the measures
    measures_raw = sparql.get_cube_measure(data['dataset'])

    measures = []
    for measure in measures_raw:
        measures.append(
            {
                'uri': measure['measureuri'],
                'label': measure['label'],
            }
        )

    output['measures'] = measures

    return HttpResponse(
        simplejson.dumps(output),
        mimetype='application/json'
    )


@csrf_exempt
def get_datasets(request):
    """
    Get the datasets for a given endpoint from the local DB.

    Return the endpoint and datasets as JSON.

    """
    data = simplejson.loads(request.body)

    response = {}

    # Add info for the selected endpoint
    selected_endpoint = Endpoint.objects.get(
        sparql_url=data['endpoint_url']
    )
    response['endpoint'] = Endpoint.objects.filter(
        sparql_url=data['endpoint_url']
    ).values(
        'label', 'website_url'
    )[0]

    # Add a list of all datasets for the selected endpoint
    response['datasets'] = list(
        Dataset.objects.filter(
            endpoint=selected_endpoint
        ).values(
            'label', 'uri', 'size'
        )
    )

    return HttpResponse(
        simplejson.dumps(response),
        mimetype='application/json'
    )


@csrf_exempt
def get_dataset_label(request):
    """Get the label of a dataset from the local DB and return as JSON."""
    data = simplejson.loads(request.body)

    response = {}

    # Get the label of the given dataset
    try:
        dataset = Dataset.objects.get(pk=data['dataset_uri'])
    except ObjectDoesNotExist:
        sparql = SPARQLQuery(data['endpoint_url'], data['search_type'])
        dataset = sparql.get_and_save_dataset_label(data['dataset_uri'])

    response['dataset'] = {
        'label': dataset.label,
        'description': dataset.description,
    }
    response['endpoint'] = {
        'label': dataset.endpoint.label,
        'website_url': dataset.endpoint.website_url,
    }

    return HttpResponse(
        simplejson.dumps(response),
        mimetype='application/json'
    )


@csrf_exempt
def save_data(request):
    """
    Turn the received tabular data into an RDF Data cube.

    Return a redirect to the specified location.

    """
    redirect_action = request.GET.get('redirect', '')

 #   cubification_request = requests.post(
 #       'http://zaire.dimis.fim.uni-passau.de:8383' +
 #       '/code-server/demo/dataextraction/headless',
 #       data=request.POST
 #   )


    #dataset = urllib.quote_plus(cubification_request.json()['dataset'])
    dataset = cubegen.create_and_save_cube(request.POST.get('htmlTable'))

    if redirect_action == 'vis':
        redirect_url = Template(
            "/vis#?dataset=$dataset&endpoint=" +
            urllib.quote_plus(settings.LOCAL_SPARQL_ENDPOINT)
        ).substitute({
            'dataset': dataset,
        })
    elif redirect_action == 'qa':
        fortytwo_id = UserMeta.objects.get(pk=request.user).fortytwo_id
        redirect_url = 'http://42-data.org/persons/' + str(fortytwo_id) + '#cubes'

    return redirect(redirect_url)


@csrf_exempt
def save_query(request):
    """
    Save the SPARQL query to 42-data.org.

    Return a redirect to the specified location.

    """
    fortytwo_id = UserMeta.objects.get(pk=request.user).fortytwo_id

    payload = {
        "personInput": {
            "id": fortytwo_id
        },
        "resourceInput": {
            "label": request.POST.get('label'),
            "description": request.POST.get('description'),
            "uri": request.POST.get('source'),
            "resourceType": "SPARQL_QUERY",
            "resourceMetaInputList": [
                {
                    "key": "SPARQL_QUERY",
                    "value": request.POST.get('sparqlQuery').replace("\r\n", "\\n").replace("\n", "\\n"),
                }
            ],
        }
    }

    headers = {'content-type': 'application/json'}

    response = requests.post(
        'http://42-data.org/resources/',
        data=simplejson.dumps(payload),
        headers=headers,
    )

    redirect_url = redirect_url = 'http://42-data.org/persons/' + str(fortytwo_id) + '#resources'

    return redirect(redirect_url)


@csrf_exempt
def save_visualization(request):
    """
    Save the visualization link to 42-data.org.

    Return a JSON object containing the redirect location.

    """
    data = simplejson.loads(request.body)

    fortytwo_id = UserMeta.objects.get(pk=request.user).fortytwo_id

    payload = {
        "personInput": {
            "id": fortytwo_id
        },
        "resourceInput": {
            "label": data['label'],
            "description": data['description'],
            "uri": data['url'],
            "resourceType": "ONLINE_RESOURCE",
        }
    }

    headers = {'content-type': 'application/json'}

    response = requests.post(
        'http://42-data.org/resources/',
        data=simplejson.dumps(payload),
        headers=headers,
    )

    response = {
        'status': 'ok',
        'redirect_url': 'http://42-data.org/persons/' + str(fortytwo_id) + '#resources',
    }

    return HttpResponse(
        simplejson.dumps(response),
        mimetype='application/json'
    )


@csrf_exempt
def aggregate(request):
    """
    Create a new RDF Data Cube based on the received parameters.

    Return a JSON object with the newly created cube.

    """
    data = simplejson.loads(request.body)

    if not data.get('label'):
        data['label'] = 'Aggregated dataset'

    sparql = SPARQLQuery(data['endpoint_url'], data['search_type'])

    response = sparql.get_aggregated_data(
        data['dataset_uri'],
        data['grouped_dimensions'],
        data['aggregated_measures']
    )

    ### Header row
    header_row = ""

    # Dimensions
    for index, dimension in enumerate(data['grouped_dimensions']):
        header_row += Template("""
        <td data-component="dimension"
        data-range="http://www.code-research.eu/resource#CubeDimensionNominal"
        data-url="$uri">
            <p>$label</p>
        </td>
        """).substitute({
            'uri': dimension['uri'],
            'label': dimension['label'],
        })

    # Measures
    unique_measure_counter = 1
    used_uris = []
    for index, measure in enumerate(data['aggregated_measures']):
        # Make sure every URI is unique
        uri = measure['uri']
        if uri in used_uris:
            uri = uri + '_' + str(unique_measure_counter)
            unique_measure_counter += 1
        used_uris.append(uri)

        header_row += Template("""
        <td data-component="observation"
        data-range="http://www.code-research.eu/resource#CubeObservationNumber"
        data-url="$uri">
          <p>$function of $label</p>
        </td>
        """).substitute({
            'uri': uri,
            'label': measure['label'],
            'function': measure['function'].title()
        })

    ### Data rows
    data_rows = ""
    for row in response['results']['results']['bindings']:
        data_rows += "<tr>"

        # Dimensions
        for index, dimension in enumerate(data['grouped_dimensions']):
            uri = ""
            if "http" in row['d' + str(index)]['value']:
                uri = row['d' + str(index)]['value']

            if row.get('d' + str(index) + 'label'):
                label = row['d' + str(index) + 'label']['value']
            else:
                label = shorten_uri(row['d' + str(index)]['value'])

            if not uri:
                uri = 'http://code-research.eu/resource/' + \
                    urllib.quote_plus(label)

            data_rows += Template(
                """
    <td data-component="dimension"
    data-range="http://www.code-research.eu/resource#CubeDimensionNominal"
    data-url="$uri">
      <p>$label</p>
    </td>
                """
            ).substitute({
                'uri': uri,
                'label': cgi.escape(label),
            })

        # Measures
        for index, measure in enumerate(data['aggregated_measures']):
            data_rows += Template(
                """
    <td data-component="observation"
    data-range="http://www.code-research.eu/resource#CubeObservationNumber">
      <p>$value</p>
    </td>
                """
            ).substitute({
                'function': measure['function'].title(),
                'value': row['m' + str(index) + 'agg']['value'],
            })

        data_rows += "</tr>"

    html_table = Template("""
    <table data-source="$source"
      data-relation="$relation"
      data-auth="$author"
      data-description="$description"
      data-label="$label">
      <tbody>
        <tr>
            $header_row
        </tr>
        $data_rows
      </tbody>
    </table>
    """).substitute({
        'header_row': header_row,
        'data_rows': data_rows,
        'source': data.get('source'),
        'relation': data.get('relation'),
        'author': data.get('importer'),
        'description': data.get('description'),
        'label': data.get('label'),
    }).replace('\n', '')

    while True:
        (html_table, occurrences) = re.subn(r'> ', r'>', html_table)
        if occurrences == 0:
            break

    while True:
        (html_table, occurrences) = re.subn(r'"  ', r'" ', html_table)
        if occurrences == 0:
            break

    html_table = html_table.strip()

    # ZAIRE Cubificatoin start:
    #cubification_request = requests.post(
    #    'http://zaire.dimis.fim.uni-passau.de:8383' +
    #    '/code-server/demo/dataextraction/headless',
    #    data={
    #        'htmlTable': html_table,
    #    }
    #)
    #aggregated_dataset_uri = urllib.quote_plus(
    #    cubification_request.json()['dataset']
    #)
    #response = {
    #    'dataset': aggregated_dataset_uri,
    #    'endpoint': 'http://zaire.dimis.fim.uni-passau.de:8890/sparql',
    #}
    # / ZAIRE Cubificatoin end.

    # Local Cubificatoin start:
    aggregated_dataset_uri = cubegen.create_and_save_cube(html_table)

    response = {
        'dataset': aggregated_dataset_uri,
        'endpoint': settings.LOCAL_SPARQL_ENDPOINT,
    }
    # / Local Cubificatoin end.

    return HttpResponse(
        simplejson.dumps(response),
        mimetype='application/json'
    )
