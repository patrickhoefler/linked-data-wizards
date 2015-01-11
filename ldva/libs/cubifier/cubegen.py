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

"""Our cool Cubifier that takes an HTML table and saves a RDF Data Cube to the Triple Store."""

from django.conf import settings
from ldva.libs.sparql.utils import SPARQLQuery
from bs4 import BeautifulSoup
import rdflib
import time
from rdflib import Graph, Literal, BNode, Namespace, RDF, RDFS, XSD, URIRef
import urllib


def get_timestamp():
    return int(round(time.time() * 1000))


def create_and_save_cube(html_table):

    print(html_table)
    """Create a RDF Data Cube based on a semantically annotated HTML table."""

    if not html_table:
        html_table = """
        <table data-auth="822" data-description="Budget and Gross Income"
        data-label="Toy Story Movies" data-relation="Query Wizard" data-source=
        "http://code.know-center.tugraz.at/search#?p0=http%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23label&amp;p0i=false&amp;p0ft=search&amp;p0fv=toy%20story&amp;p1=http%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23type&amp;p1i=false&amp;p2=http%3A%2F%2Fdbpedia.org%2Fontology%2Fbudget&amp;p2i=false&amp;p2ft=not_empty&amp;p2fv=1&amp;p3=http%3A%2F%2Fdbpedia.org%2Fontology%2Fgross&amp;p3i=false&amp;endpoint=http%3A%2F%2Fdbpedia.org%2Fsparql&amp;searchtype=virtuoso"
        id="results">
            <tbody>
                <tr>
                    <td data-component="dimension" data-url=
                    "http://www.w3.org/2000/01/rdf-schema#label">
                        <p>Label</p>
                    </td>

                    <td data-component="observation" data-url=
                    "http://dbpedia.org/ontology/budget">
                        <p>Budget ($)</p>
                    </td>

                    <td data-component="observation" data-url=
                    "http://dbpedia.org/ontology/gross">
                        <p>Gross ($)</p>
                    </td>
                </tr>

                <tr>
                    <td data-component="dimension" data-inverse="false" data-p=
                    "http://www.w3.org/2000/01/rdf-schema#label" data-range=
                    "http://code-research.eu/resource#CubeDimensionNominal" data-s=
                    "http://dbpedia.org/resource/Toy_Story" data-url=
                    "http://dbpedia.org/resource/Toy_Story">
                        <p>Toy Story</p>
                    </td>

                    <td data-component="observation" data-inverse="false" data-p=
                    "http://dbpedia.org/ontology/budget" data-range=
                    "http://code-research.eu/resource#CubeObservationNumber"
                    data-s="http://dbpedia.org/resource/Toy_Story" data-url=
                    "http://dbpedia.org/resource/Toy_Story">
                        <p>30000000</p>
                    </td>

                    <td data-component="observation" data-inverse="false" data-p=
                    "http://dbpedia.org/ontology/gross" data-range=
                    "http://code-research.eu/resource#CubeObservationNumber"
                    data-s="http://dbpedia.org/resource/Toy_Story" data-url=
                    "http://dbpedia.org/resource/Toy_Story">
                        <p>361958736</p>
                    </td>
                </tr>

                <tr>
                    <td data-component="dimension" data-inverse="false" data-p=
                    "http://www.w3.org/2000/01/rdf-schema#label" data-range=
                    "http://code-research.eu/resource#CubeDimensionNominal" data-s=
                    "http://dbpedia.org/resource/Toy_Story_2" data-url=
                    "http://dbpedia.org/resource/Toy_Story_2">
                        <p>Toy Story 2</p>
                    </td>

                    <td data-component="observation" data-inverse="false" data-p=
                    "http://dbpedia.org/ontology/budget" data-range=
                    "http://code-research.eu/resource#CubeObservationNumber"
                    data-s="http://dbpedia.org/resource/Toy_Story_2" data-url=
                    "http://dbpedia.org/resource/Toy_Story_2">
                        <p>90000000</p>
                    </td>

                    <td data-component="observation" data-inverse="false" data-p=
                    "http://dbpedia.org/ontology/gross" data-range=
                    "http://code-research.eu/resource#CubeObservationNumber"
                    data-s="http://dbpedia.org/resource/Toy_Story_2" data-url=
                    "http://dbpedia.org/resource/Toy_Story_2">
                        <p>485015179</p>
                    </td>
                </tr>

                <tr>
                    <td data-component="dimension" data-inverse="false" data-p=
                    "http://www.w3.org/2000/01/rdf-schema#label" data-range=
                    "http://code-research.eu/resource#CubeDimensionNominal" data-s=
                    "http://dbpedia.org/resource/Toy_Story_3" data-url=
                    "http://dbpedia.org/resource/Toy_Story_3">
                        <p>Toy Story 3</p>
                    </td>

                    <td data-component="observation" data-inverse="false" data-p=
                    "http://dbpedia.org/ontology/budget" data-range=
                    "http://code-research.eu/resource#CubeObservationNumber"
                    data-s="http://dbpedia.org/resource/Toy_Story_3" data-url=
                    "http://dbpedia.org/resource/Toy_Story_3">
                        <p>200000000</p>
                    </td>

                    <td data-component="observation" data-inverse="false" data-p=
                    "http://dbpedia.org/ontology/gross" data-range=
                    "http://code-research.eu/resource#CubeObservationNumber"
                    data-s="http://dbpedia.org/resource/Toy_Story_3" data-url=
                    "http://dbpedia.org/resource/Toy_Story_3">
                        <p>1063171911</p>
                    </td>
                </tr>
            </tbody>
        </table>
        """
        
        print "******************** html table ************************"
        print html_table
        print "******************** end html table ************************"
    ###########################################################################
    # Read the table
    # http://www.crummy.com/software/BeautifulSoup/

    soupParser = BeautifulSoup(html_table)

    # Label will serve to name the dsd and the dataset
    table = soupParser.find('table')
    label = table['data-label']
    description = table['data-description']

    # header contains dimensions and measures
    header = soupParser.find('tr')
    headerComponents = []
    dCount = 0
    mCount = 0
    timestamp = get_timestamp()

    print("************************ BEAUTIFUL SOUP ************************ ")

    for h in header.find_all('td'):
        if h['data-component'] == 'dimension':
            headerComponents.append(
                {
                    'value': h.find('p').string,
                    'type': 'dimension',
                    'id': 'dimension_' + str(dCount) + '_' + str(timestamp),
                    'uri': h['data-url'],
                }
            )
            dCount = dCount + 1
            print "data-url = ", h['data-url']

        if h['data-component'] == 'observation':
            headerComponents.append(
                {
                    'value': h.find('p').string,
                    'type': 'measure',
                    'id': 'measure_' + str(mCount) + '_' + str(timestamp),
                    'uri': h['data-url'],
                }
            )
            mCount = mCount + 1

    # Observations

    # Create the namespaces
    QB = Namespace("http://purl.org/linked-data/cube#")
    CODE = Namespace("http://code-research.eu/resource/")
    VA = Namespace("http://code-research.eu/ontology/visual-analytics#")
    SDMX_MEASURE = Namespace("http://purl.org/linked-data/sdmx/2009/measure#")
    # OWL = Namespace("http://www.w3.org/2002/07/owl#")

    observations = soupParser.find_all('tr')
    obsComponents = []
    firstTableRow = True

    for o in observations:
        # The first table row contains the structure and no observations
        if firstTableRow:
            firstTableRow = False
            continue  # to the next round of the loop

        anObs = []
        for i, item in enumerate(o.find_all('td')):
            value = str(item.find('p').string)
            item_value = value

            value = urllib.quote_plus(value)
            item_id = value + '_' + str(timestamp)
            item_obs_type = headerComponents[i]['type']
            item_parent = CODE[headerComponents[i]['id']]
            if item_obs_type == 'dimension' and headerComponents[i].get('uri'):
                item_parent = URIRef(headerComponents[i].get('uri'))
            anObs.append(
                {
                    'id': item_id,
                    'uri': item.get('data-url'),
                    'value': item_value,
                    'parent': item_parent,
                    'obs-type': item_obs_type,
                }
            )

        obsComponents.append(anObs)

    print obsComponents

    ###########################################################################
    # Create the RDF Data Cube
    # http://rdflib.readthedocs.org/en/latest/intro_to_creating_rdf.html

    g = Graph()

    # dataset = URIRef('dataset_' + str(urllib.quote_plus(label)) + '_' + str(timestamp))
    dataset = URIRef('dataset_' + str(timestamp))
    # dsd = URIRef('dsd_' + str(urllib.quote_plus(label)) + '_' + str(timestamp))
    dsd = URIRef('dsd_' + str(timestamp))

    ### Dsd definition
    g.add((CODE[dsd], RDF.type, QB.DataStructureDefinition))

    ### Components
    for c in headerComponents:
        id = c['id']
        component = 'component_' + id

        g.add((CODE[dsd], QB.component, CODE[component]))

        if c['type'] == 'dimension':
            tempSubject = CODE[id]
            if c.get('uri'):
                tempSubject = URIRef(c.get('uri'))

            g.add((CODE[component], QB.dimension, tempSubject))
        else:
            g.add((CODE[component], QB.measure, CODE[id]))

        g.add((CODE[component], RDFS.label, Literal(str(c['value']), lang='en')))

    ### Dimensions & measures
    for c in headerComponents:
        id = c['id']

        # if c.get('uri'):
        #     g.add((CODE[id], OWL.equivalentProperty, URIRef(c.get('uri'))))

        if c['type'] == 'dimension':
            tempSubject = CODE[id]
            if c.get('uri'):
                tempSubject = URIRef(c.get('uri'))
            g.add((tempSubject, RDF.type, RDF.Property))
            g.add((tempSubject, RDF.type, QB.DimensionProperty))
            g.add((tempSubject, RDFS.label, Literal(str(c['value']), lang='en')))
            g.add((tempSubject, RDFS.subPropertyOf, VA.cubeDimensionNominal))
            g.add((tempSubject, RDFS.range, XSD.string))
        else:
            g.add((CODE[id], RDF.type, RDF.Property))
            g.add((CODE[id], RDF.type, QB.MeasureProperty))
            g.add((CODE[id], RDFS.label, Literal(str(c['value']), lang='en')))
            g.add((CODE[id], RDFS.subPropertyOf, SDMX_MEASURE.obsValue))
            g.add((CODE[id], RDFS.range, XSD.decimal))

    ### Dataset definition
    g.add((CODE[dataset], RDF.type, QB.DataSet))
    g.add((CODE[dataset], RDFS.label, Literal(str(label))))
    g.add((CODE[dataset], RDFS.comment, Literal(str(description))))
    g.add((CODE[dataset], QB.structure, CODE[dsd]))

    ### Observations

    obsCount = 0

    for o in obsComponents:
        # Add observation
        observation = 'obs_' + str(obsCount) + '_' + str(timestamp)
        g.add((CODE[observation], RDF.type, QB.Observation))

        for item in o:

            parent = item['parent']
            if item['obs-type'] == 'dimension':
                entity = 'entity_' + item['id']
                # Add entity
                g.add((CODE[entity], RDF.type, CODE.Entity))
                g.add((CODE[entity], RDFS.label, Literal(str(item['value']))))

                # if item.get('uri'):
                #     g.add((CODE[entity], OWL.sameAs, URIRef(item.get('uri'))))

                # Add entity to observation
                g.add((CODE[observation], parent, CODE[entity]))

            else:
                # Add number measured to observation
                g.add((CODE[observation], parent, Literal(float(item['value']))))

        g.add((CODE[observation], QB.dataSet, CODE[dataset]))
        obsCount = obsCount + 1

    ### Prefix binding

    g.bind('qb', URIRef("http://purl.org/linked-data/cube#"))
    g.bind('code', URIRef("http://code-research.eu/resource/"))
    g.bind('va', URIRef("http://code-research.eu/ontology/visual-analytics#"))
    g.bind('sdmx-measure', URIRef("http://purl.org/linked-data/sdmx/2009/dimension#"))
    # g.bind('owl', URIRef("http://www.w3.org/2002/07/owl#"))

    serialized_graph = g.serialize(format='nt')
    print("************************ CUBE ******************************* ")
    print(g.serialize(format='nt'))

    # Save the Cube to Virtuoso
    sparql = SPARQLQuery(settings.LOCAL_SPARQL_ENDPOINT, 'virtuoso')

    query = "INSERT DATA INTO GRAPH <http://code-research.eu/graph/" + str(timestamp) + "> {\n"
    query += serialized_graph
    query += "}"

    response = sparql.update(query)

    # Return some status message
    if response['results']['bindings'][0]['callret-0']['value']:
        return str(CODE[dataset])
    else:
        return "Looks like it didn't work ..."
