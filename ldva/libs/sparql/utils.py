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

"""Collection of SPARQL utils."""

import collections
import math
import re
from SPARQLWrapper import SPARQLWrapper, POST, JSON, SELECT
from string import Template
import time

from ldva.libs.sparql.models import Dataset, Endpoint, Log


class SPARQLQuery:

    """Helper class for handling SPARQL queries."""

    def __init__(self, endpoint_url, search_type='regex'):
        """Initialze the object with the endpoint URI and the search type."""
        self.endpoint_url = endpoint_url
        self.search_type = search_type
        self.batch_size = 10

    def query(self, query, virtuoso=False):
        """
        Send a SPARQL query to the previously set endpoint.

        Returns a dictionary with the results.

        """
        sparql = SPARQLWrapper(self.endpoint_url)
        sparql.setMethod(POST)
        sparql.setReturnFormat(JSON)
        # Since the SPARQLWrapper doesn't like unicode:
        sparql.setQuery(query.encode('utf-8'))
        if virtuoso:
            sparql.queryType = SELECT
        return sparql.query().convert()

    def get_subjects(self, predicates, offset, dataset):
        """
        Get the RDF entities (subjects) for the given request.

        Returns a dictionary with the results and some meta info.

        """
        response = {}

        where_clause = self.get_subjects_where_clause(predicates, dataset)

        # Workaround for Apache Marmotta
        if self.search_type == 'marmotta':
            distinct = ''
            prefixes = 'PREFIX mm: <http://marmotta.apache.org/vocabulary/sparql-functions#>\n'
        else:
            distinct = 'DISTINCT '
            prefixes = ''

        response['query'] = Template(
            """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX qb: <http://purl.org/linked-data/cube#>
            $prefixes
            SELECT ${distinct}?s
            $where_clause
            LIMIT $batch_size
            OFFSET $offset"""
        ).substitute({
            'prefixes': prefixes,
            'distinct': distinct,
            'where_clause': where_clause,
            'batch_size': self.batch_size,
            'offset': offset,
        }).replace('            ', '')

        start = time.time()
        response['results'] = self.query(response['query'])
        response['time'] = round(time.time() - start, 2)

        # Create a list of subjects
        response['subjects'] = []
        for item in response['results']['results']['bindings']:
            response['subjects'].append(item['s']['value'])

        # Log the SPARQL query
        Log.objects.create(
            type='get_subjects',
            sparql_query=response['query'],
            runtime=response['time'],
            result_count=len(response['subjects']),
            endpoint=self.endpoint_url,
        )

        response['endpoint_url'] = self.endpoint_url

        # Return
        return response

    def get_subjects_count(self, predicates, dataset):
        """
        Get the count of the RDF entities (subjects) for the given request.

        Returns a dictionary with the subjects count and some meta info.

        """
        response = {}

        where_clause = self.get_subjects_where_clause(
            predicates,
            dataset,
            order=False
        )

        # Workaround for Apache Marmotta
        if self.search_type == 'marmotta':
            distinct = ''
            prefixes = 'PREFIX mm: <http://marmotta.apache.org/vocabulary/sparql-functions#>\n'
        else:
            distinct = 'DISTINCT '
            prefixes = ''

        response['query'] = Template(
            """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX qb: <http://purl.org/linked-data/cube#>
            $prefixes
            SELECT (COUNT(${distinct}?s) as ?count)
            $where_clause
            """
        ).substitute({
            'prefixes': prefixes,
            'distinct': distinct,
            'where_clause': where_clause,
        }).replace('            ', '')

        start = time.time()
        response['results'] = self.query(response['query'])
        response['time'] = round(time.time() - start, 2)

        # Add the results count to the response object
        response['count'] = 0
        if response['results']['results']['bindings']:
            response['count'] = \
                response['results']['results']['bindings'][0]['count']['value']

        # If we're in dataset mode and we have received results,
        # update the observations count in the local DB
        if dataset and response['count'] > 0:
            dataset_object = Dataset.objects.get(pk=dataset)
            dataset_object.size = response['count']
            dataset_object.save()

        # Log the SPARQL query
        Log.objects.create(
            type='get_subjects_count',
            sparql_query=response['query'],
            runtime=response['time'],
            result_count=response['count'],
            endpoint=self.endpoint_url,
        )

        # Return
        return response

    def get_subjects_where_clause(self, predicates, dataset,
                                  order=True, language='en'):
        """Build and return the where clause."""

        filter_counter = -1
        where_clause = 'WHERE {'

        # Iterate over the predicate filters
        for predicate in predicates:
            if (self.search_type == 'bigdata' and
                    predicate.get('filter_type') == 'search'):
                filter_counter += 1
                where_clause += Template(
                    """
                    # Default fulltext search for BigData endpoints
                    ?s <$p> ?regex$filter_counter .
                    ?regex$filter_counter <http://www.bigdata.com/rdf/search#search> '$filter_value' .
                    ?regex$filter_counter <http://www.bigdata.com/rdf/search#matchAllTerms> 'true' .
                    ?regex$filter_counter <http://www.bigdata.com/rdf/search#rank> ?rank$filter_counter ."""
                ).substitute({
                    'p': predicate['uri'],
                    'filter_counter': filter_counter,
                    'filter_value': predicate['filter_value'].replace('"', ''),
                }).replace('                ', '')

            elif (self.search_type == 'regex' and
                    predicate.get('filter_type') == 'search'):
                filter_counter += 1
                where_clause += Template(
                    """
                    # Worst case: Let's do a regex search
                    ?s <$p> ?regex$filter_counter .
                    FILTER regex(?regex$filter_counter, '$filter_val', 'i')"""
                ).substitute({
                    'p': predicate['uri'],
                    'filter_counter': filter_counter,
                    'filter_val': predicate['filter_value'].replace('"', ''),
                }).replace('            ', '')

            elif (self.search_type == 'owlim' and
                    predicate.get('filter_type') == 'search'):
                filter_counter += 1
                where_clause += Template(
                    """
                    # Fulltext search for OWLIM endpoints
                    ?s <$p> ?regex$filter_counter .
                    ?regex$filter_counter <http://www.ontotext.com/owlim/lucene#> '$filter_value' ."""
                ).substitute({
                    'p': predicate['uri'],
                    'filter_counter': filter_counter,
                    'filter_value': predicate['filter_value'].replace('"', ''),
                }).replace('            ', '')

            elif (self.search_type == 'lld' and
                    predicate.get('filter_type') == 'search'):
                filter_counter += 1
                where_clause += Template(
                    """
                    # Special fulltext search for Linked Life Data endpoint
                    ?s <$p> ?regex$f_counter .
                    ?regex$f_counter <http://www.ontotext.com/owlim/lucene#lldLiterals> '$f_value' ."""
                ).substitute({
                    'p': predicate['uri'],
                    'f_counter': filter_counter,
                    'f_value': predicate['filter_value'].replace('"', ''),
                }).replace('            ', '')

            elif (self.search_type == 'virtuoso' and
                    predicate.get('filter_type') == 'search'):
                filter_counter += 1
                where_clause += Template(
                    """
                    # Fulltext search for Virtuoso endpoints
                    ?s <$p> ?regex$filter_counter
                    FILTER (
                        LANG(?regex$filter_counter) = '' ||
                        LANGMATCHES(LANG(?regex$filter_counter), '$language')
                    ) .
                    ?regex$filter_counter bif:contains '"$filter_value"'
                    OPTION (score ?score$filter_counter) ."""
                ).substitute({
                    'p': predicate['uri'],
                    'filter_counter': filter_counter,
                    'filter_value': predicate['filter_value'].replace('"', ''),
                    'language': language,
                }).replace('                ', '')

            elif (self.search_type == 'marmotta' and
                    predicate.get('filter_type') == 'search'):
                filter_counter += 1
                where_clause += Template(
                    """
                    # Fulltext search for Apache Marmotta endpoints
                    ?s <$p> ?regex$filter_counter
                    FILTER (
                        LANG(?regex$filter_counter) = '' ||
                        LANGMATCHES(LANG(?regex$filter_counter), '$language')
                    )
                    FILTER ( mm:fulltext-search(str(?regex$filter_counter), '$filter_value') ) ."""
                ).substitute({
                    'p': predicate['uri'],
                    'filter_counter': filter_counter,
                    'filter_value': predicate['filter_value'].replace('"', ''),
                    'language': language,
                }).replace('                ', '')

            elif predicate.get('filter_type') == 'uri':
                if not predicate.get('inverse'):
                    uri_filter_template = Template('    ?s <$p> <$o> .')
                else:
                    uri_filter_template = Template('    <$o> <$p> ?s .')
                where_clause += '\n    # URI filter\n'
                where_clause += uri_filter_template.substitute({
                    'p': predicate['uri'],
                    'o': predicate['filter_value'].replace('"', ''),
                })

            elif predicate.get('filter_type') == 'date':
                filter_counter += 1
                # Prepare the date filter
                where_clause += Template(
                    '\n    # Date filter\n    ?s <$p> ?o$filter_counter .\n'
                ).substitute({
                    'p': predicate['uri'],
                    'filter_counter': filter_counter,
                })

                minmax = predicate['filter_value'].partition(',')
                # A minimum value is set
                if minmax[0]:
                    where_clause += Template(
                        """
                        FILTER (?o$filter_counter >= '${min}'^^xsd:date)"""
                    ).substitute({
                        'filter_counter': filter_counter,
                        'min': minmax[0],
                    }).replace('                    ', '')

                # A maximum value is set
                if minmax[2]:
                    where_clause += Template(
                        """
                        FILTER (?o$filter_counter <= '${max}'^^xsd:date)"""
                    ).substitute({
                        'filter_counter': filter_counter,
                        'max': minmax[2],
                    }).replace('                    ', '')

            elif predicate.get('filter_type') == 'datetime':
                filter_counter += 1
                # Prepare the date filter
                where_clause += Template(
                    '\n    # Date filter\n    ?s <$p> ?o$filter_counter .\n'
                ).substitute({
                    'p': predicate['uri'],
                    'filter_counter': filter_counter,
                })

                minmax = predicate['filter_value'].partition(',')
                # A minimum value is set
                if minmax[0]:
                    where_clause += Template(
                        """
                        FILTER (?o$filter_counter >= '${min}'^^xsd:dateTime)"""
                    ).substitute({
                        'filter_counter': filter_counter,
                        'min': minmax[0],
                    }).replace('                    ', '')

                # A maximum value is set
                if minmax[2]:
                    where_clause += Template(
                        """
                        FILTER (?o$filter_counter <= '${max}'^^xsd:dateTime)"""
                    ).substitute({
                        'filter_counter': filter_counter,
                        'max': minmax[2],
                    }).replace('                    ', '')

            elif predicate.get('filter_type') == 'numeric':
                filter_counter += 1
                # Prepare the numeric filter
                where_clause += Template(
                    '\n    # Numeric filter\n    ?s <$p> ?o$filter_counter .\n'
                ).substitute({
                    'p': predicate['uri'],
                    'filter_counter': filter_counter,
                })

                minmax = predicate['filter_value'].partition(',')
                # A minimum value is set
                if minmax[0]:
                    where_clause += Template(
                        '    FILTER (?o$filter_counter >= $min)'
                    ).substitute({
                        'filter_counter': filter_counter,
                        'min': minmax[0],
                    })

                # A maximum value is set
                if minmax[2]:
                    where_clause += Template(
                        '    FILTER (?o$filter_counter <= $max)'
                    ).substitute({
                        'filter_counter': filter_counter,
                        'max': minmax[2],
                    })

            elif predicate.get('filter_type') == 'not_empty':
                filter_counter += 1

                if not predicate.get('inverse'):
                    not_empty_template = Template(
                        """
                        ?s <$p> ?o$filter_counter .
                        FILTER ( bound( ?o$filter_counter ) )"""
                    )
                else:
                    not_empty_template = Template(
                        """
                        ?o$filter_counter <$p> ?s .
                        FILTER ( bound( ?o$filter_counter ) )"""
                    )

                where_clause += '\n    # "Not empty" filter'
                where_clause += not_empty_template.substitute({
                    'p': predicate['uri'],
                    'filter_counter': filter_counter,
                }).replace('                    ', '')

        # Check if we're in dataset mode
        if dataset:
            where_clause += Template(
                """
                # RDF Data Cube clause
                ?s rdf:type qb:Observation .
                ?s qb:dataSet <$dataset> ."""
            ).substitute({
                'dataset': dataset,
            }).replace('            ', '')

        # Close WHERE clause
        where_clause += '\n}'

        if order and self.search_type != 'marmotta':
            # Set ORDER BY depending on the search type
            if self.search_type == 'bigdata' and filter_counter >= 0:
                order_by = '?rank0'
            elif self.search_type == 'virtuoso' and filter_counter >= 0:
                order_by = 'DESC(?score0) ?s'
            else:
                order_by = '?s'

            where_clause += Template(
                '\nORDER BY $order_by'
            ).substitute({
                'order_by': order_by,
            })

        return where_clause

    def get_predicates(self, subjects, language='en'):
        """
        Get the used properties (predicates) for the given list of subjects.

        Returns a dictionary with the results and some meta info.

        """
        response = {}

        # Query the relevant predicates
        # Workaround for Apache Marmotta
        if self.search_type == 'marmotta':
            response['query'] = ''
        else:
            response['query'] = \
                'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n\n'
        response['query'] += 'SELECT ?p ?p_inverse ?label\n'
        response['query'] += 'WHERE {\n'

        # Limit to current named graph
        # Workaround for Apache Marmotta
        if self.search_type != 'marmotta':
            response['query'] += '  GRAPH ?g {'

        # Build patterns for union
        patterns = []
        for subject in subjects:
            patterns.append(
                Template(
                    """
                        {
                          <$subject> ?p [] .
                          OPTIONAL {
                            ?p rdfs:label ?label
                            FILTER (
                              LANG(?label) = '' ||
                              LANGMATCHES(LANG(?label), '$language')
                            ) .
                          }
                        }
                    """
                ).substitute({
                    'subject': subject,
                    'language': language,
                }).replace('                    ', '')
            )
            patterns.append(
                Template(
                    """
                        {
                          [] ?p_inverse <$subject> .
                          OPTIONAL {
                            ?p_inverse rdfs:label ?label
                            FILTER (
                              LANG(?label) = '' ||
                              LANGMATCHES(LANG(?label), '$language')
                            ) .
                          }
                        }
                    """
                ).substitute({
                    'subject': subject,
                    'language': language,
                }).replace('                    ', '')
            )

        # Join union patterns
        response['query'] += '    UNION'.join(patterns)

        # End of named graph
        # Workaround for Apache Marmotta
        if self.search_type != 'marmotta':
            response['query'] += '  }\n'

        # End of where clause
        response['query'] += '}'

        start = time.time()
        response['results'] = self.query(response['query'])
        response['time'] = round(time.time() - start, 2)

        # Create a list of all predicates
        response['predicates'] = []
        for item in response['results']['results']['bindings']:
            if item.get('label'):
                label = item['label']['value']
                label = label[:1].upper() + label[1:]
            else:
                if item.get('p'):
                    label = shorten_uri(item['p']['value'])
                elif item.get('p_inverse'):
                    label = shorten_uri(item['p_inverse']['value'])
            if item.get('p'):
                response['predicates'].append({
                    'uri': item['p']['value'],
                    'label': label,
                    'inverse': False,
                })
            elif item.get('p_inverse'):
                response['predicates'].append({
                    'uri': item['p_inverse']['value'],
                    'label': generate_inverse_label(label),
                    'inverse': True,
                })

        # Log the SPARQL query
        Log.objects.create(
            type='get_predicates',
            sparql_query=response['query'],
            runtime=response['time'],
            result_count=len(response['predicates']),
            endpoint=self.endpoint_url,
        )

        # Return
        return response

    def get_objects(self, subjects, predicate, language='en'):
        """
        Get the details (objects) for the given subjects and predicate.

        Return a dictionary with the results and some meta info.

        """
        response = {}

        # Let's start with the prefixes
        # Workaround for Apache Marmotta
        if self.search_type == 'marmotta':
            response['query'] = ''
        else:
            response['query'] = \
                'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n\n'

        # Create the bindings
        bindings = []
        for i in range(len(subjects)):
            bindings.append('?o' + str(i))
            bindings.append('?label' + str(i))

        response['query'] += 'SELECT DISTINCT ' + ' '.join(bindings) + '\n'

        # Start of where clause
        response['query'] += 'WHERE {'

        # Build patterns for union
        patterns = []
        for i in range(len(subjects)):
            if not predicate['inverse']:
                spo_template = Template("<$subject> <$predicate> ?o$i .")
            elif predicate['inverse']:
                spo_template = Template("?o$i <$predicate> <$subject> .")

            spo_clause = spo_template.substitute({
                'subject': subjects[i],
                'predicate': predicate['uri'],
                'i': i,
            })

            pattern = Template(
                """
                {
                  $spo_clause
                  OPTIONAL { ?o$i rdfs:label ?label$i . }
                  FILTER (
                    (
                      !ISLITERAL(?o$i) && (
                        !BOUND(?label$i) ||
                        LANG(?label$i) = '' ||
                        LANGMATCHES(LANG(?label$i), '$language')
                      )
                    ) ||
                    LANG(?o$i) = '' ||
                    LANGMATCHES(LANG(?o$i), '$language')
                  )
                }\n"""
            ).substitute({
                'spo_clause': spo_clause,
                'i': i,
                'language': language,
            })
            pattern = re.sub(
                re.compile(r'^              ', re.MULTILINE),
                '',
                pattern
            )
            patterns.append(pattern)

        # Join union patterns
        response['query'] += '  UNION'.join(patterns)

        # End of where clause
        response['query'] += '}'

        # Submit the query
        start = time.time()
        response['results'] = self.query(response['query'])
        response['time'] = round(time.time() - start, 2)

        # Log the SPARQL query
        Log.objects.create(
            type='get_objects',
            sparql_query=response['query'],
            runtime=response['time'],
            result_count=len(response['results']['results']['bindings']),
            endpoint=self.endpoint_url,
        )

        # Build objects table
        response['table'] = []

        # Iterate through the results
        for row in response['results']['results']['bindings']:
            table_row = {}
            table_row['o'] = {}

            # We received either o{i} or label{i}
            for key, value in row.iteritems():
                if 'o' in key:
                    table_row['s'] = subjects[int(key.replace('o', ''))]
                    table_row['p'] = predicate
                    table_row['o']['value'] = value['value']
                    table_row['o']['type'] = value['type']

                    if value.get('datatype'):
                        table_row['o']['datatype'] = value.get('datatype')

                elif 'label' in key:
                    table_row['o']['label'] = value

            # If there is no label, generate one programmatically
            if (table_row['o']['type'] == 'uri' and
                    not table_row['o'].get('label')):
                table_row['o']['label'] = {
                    'value': shorten_uri(table_row['o']['value'])
                }

            response['table'].append(table_row)

        return response

    def get_comprehensive_sparql_query(self, predicates, dataset,
                                       order=False, language='en'):
        """Create and return one SPARQL query to rule them all."""

        where_clause = self.get_subjects_where_clause(
            predicates, dataset, order, language
        )

        select_objects = ''
        objects_clause = ''

        for i in range(len(predicates)):
            select_objects += Template(
                ' ?object$i ?label$i'
            ).substitute({
                'i': i,
            })

            if not predicates[i]['inverse']:
                spo_template = Template("    ?s <$predicate> ?object$i .")
            elif predicates[i]['inverse']:
                spo_template = Template("    ?object$i <$predicate> ?s .")

            spo_clause = spo_template.substitute({
                'predicate': predicates[i]['uri'],
                'i': i,
            })

            label_clause = Template(
                """
                    OPTIONAL { ?object$i rdfs:label ?label$i . }
                    FILTER (
                      (
                        !ISLITERAL(?object$i) && (
                          !BOUND(?label$i) ||
                          LANG(?label$i) = '' ||
                          LANGMATCHES(LANG(?label$i), '$language')
                        )
                      ) ||
                      LANG(?object$i) = '' ||
                      LANGMATCHES(LANG(?object$i), '$language')
                    )
                """
            ).substitute({
                'i': i,
                'language': language,
            }).replace('                ', '')

            objects_clause += spo_clause + label_clause

        # Workaround for Apache Marmotta
        if self.search_type == 'marmotta':
            prefixes = """PREFIX mm: <http://marmotta.apache.org/vocabulary/sparql-functions#>"""
        else:
            prefixes = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX qb: <http://purl.org/linked-data/cube#>"""

        query = Template("""$prefixes

            """).substitute({
            'prefixes': prefixes,
        })
        query = query.replace('            ', '')

        query += 'SELECT DISTINCT ?s' + select_objects + '\n'
        query += where_clause

        query = re.sub(
            re.compile(r'^}', re.MULTILINE),
            '    # Objects\n' + objects_clause + '}',
            query
        )

        return query

    def get_aggregated_data(self, dataset,
                            grouped_dimensions, aggregated_measures):
        """
        Get the aggregated data from the SPARQL endpoint.

        Return a dictionary with the results and some meta info.

        """
        response = {}

        select = ''
        where = ''

        for index, dimension in enumerate(grouped_dimensions):

            # SELECT
            select += '?d' + str(index) + ' ?d' + str(index) + 'label '
            # WHERE
            where += Template("""
            ?s <$uri> ?d$index .
            OPTIONAL { ?d$index rdfs:label ?d${index}label . }
            """).substitute({
                'uri': dimension['uri'],
                'index': index,
            })

        group_by = select

        for index, measure in enumerate(aggregated_measures):
            # SELECT
            if measure['function'] == 'avg':
                select += '(AVG(xsd:double(?m'
            elif measure['function'] == 'count':
                select += '(COUNT(xsd:double(?m'
            elif measure['function'] == 'max':
                select += '(MAX(xsd:double(?m'
            elif measure['function'] == 'min':
                select += '(MIN(xsd:double(?m'
            elif measure['function'] == 'sum':
                select += '(SUM(xsd:double(?m'
            select += str(index) + ')) as ?m' + str(index) + 'agg) '

            # WHERE
            where += Template(
                """
                ?s <$uri> ?m$index .
                """
            ).substitute({
                'uri': measure['uri'],
                'index': index,
            })

        response['query'] = Template(
            """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX qb: <http://purl.org/linked-data/cube#>

            SELECT $select
            WHERE {
                ?s rdf:type qb:Observation .
                ?s qb:dataSet <$dataset> .
                $where
            }
            GROUP BY $group_by
            """
        ).substitute({
            'select': select,
            'dataset': dataset,
            'select': select,
            'where': where,
            'group_by': group_by,
        })

        start = time.time()
        response['results'] = self.query(response['query'])
        response['time'] = round(time.time() - start, 2)

        return response

    def refresh_dataset_list(self):
        """
        Retrieve and save all RDF Data Cube datasets from the given endpoint.

        Return nothing.

        """
        datasets = {}

        # Query the cube dataset metadata
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dc: <http://purl.org/dc/terms/>
        PREFIX qb: <http://purl.org/linked-data/cube#>

        SELECT ?dataset ?label ?title ?comment ?description
        WHERE {
            ?dataset rdf:type qb:DataSet .
            OPTIONAL { ?dataset rdfs:label ?label } .
            OPTIONAL { ?dataset dc:title ?title } .
            OPTIONAL { ?dataset rdfs:comment ?comment } .
            OPTIONAL { ?dataset dc:description ?description } .
        }
        """

        # Submit the query
        start = time.time()
        results = self.query(query)
        runtime = round(time.time() - start, 2)

        # Log the SPARQL query
        Log.objects.create(
            type='refresh_dataset_list__meta',
            sparql_query=query,
            runtime=runtime,
            result_count=len(results['results']['bindings']),
            endpoint=self.endpoint_url,
        )

        # Delete all datasets that belong to the current endpoint from the DB
        Dataset.objects.filter(
            endpoint=Endpoint.objects.get(sparql_url=self.endpoint_url)
        ).delete()

        # Did we find any datasets?
        if len(results['results']['bindings']) > 0:

            # Extract the metadata and save to dictionary
            for dataset in results['results']['bindings']:
                dataset_uri = dataset['dataset']['value']
                dataset_label = ''
                if 'label' in dataset.keys():
                    dataset_label = dataset['label']['value']
                elif 'title' in dataset.keys():
                    dataset_label = dataset['title']['value']

                dataset_description = ''
                if 'description' in dataset.keys():
                    dataset_description = dataset['description']['value']
                elif 'comment' in dataset.keys():
                    dataset_description = dataset['comment']['value']

                datasets[dataset_uri] = {
                    'label': dataset_label,
                    'description': dataset_description,
                }

            # Workaround: The 270a endpoints don't deliver observation counts
            if self.endpoint_url.find('270a') == -1:

                # Query the cube dataset observation count
                query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX dc: <http://purl.org/dc/terms/>
                PREFIX qb: <http://purl.org/linked-data/cube#>

                SELECT ?dataset (COUNT(?observation) AS ?observation_count)
                WHERE {
                    ?dataset rdf:type qb:DataSet .
                    ?observation rdf:type qb:Observation .
                    ?observation qb:dataSet ?dataset .
                }
                GROUP BY ?dataset
                """

                # Submit the query
                start = time.time()
                results = self.query(query)
                runtime = round(time.time() - start, 2)

                # Log the SPARQL query
                Log.objects.create(
                    type='refresh_dataset_list__count',
                    sparql_query=query,
                    runtime=runtime,
                    result_count=len(results['results']['bindings']),
                    endpoint=self.endpoint_url,
                )

                # Extract the observation count and save to dictionary
                for dataset in results['results']['bindings']:
                    dataset_uri = dataset['dataset']['value']
                    datasets[dataset_uri]['size'] = \
                        dataset['observation_count']['value']

            # Save the received datasets to the DB
            for key, dataset in datasets.iteritems():
                # Workaround: If we received no observation count, set to 0
                if 'size' not in dataset.keys():
                    dataset['size'] = 0
                # Create and save the datasets
                Dataset.objects.create(
                    pk=key,
                    endpoint=Endpoint.objects.get(
                        sparql_url=self.endpoint_url
                    ),
                    label=dataset['label'][:1].upper() + dataset['label'][1:],
                    description=dataset['description'],
                    size=dataset['size']
                )

    def get_and_save_dataset_label(self, dataset_uri):
        """
        Retrieve and save the label and description of a given dataset.

        Return the dataset object.

        """

        # Query the cube dataset metadata
        query = Template("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dc: <http://purl.org/dc/terms/>
        PREFIX qb: <http://purl.org/linked-data/cube#>

        SELECT ?label ?title ?comment ?description
        WHERE {
            <$dataset_uri> rdf:type qb:DataSet .
            OPTIONAL { <$dataset_uri> rdfs:label ?label } .
            OPTIONAL { <$dataset_uri> dc:title ?title } .
            OPTIONAL { <$dataset_uri> rdfs:comment ?comment } .
            OPTIONAL { <$dataset_uri> dc:description ?description } .
        }
        """).substitute({
            'dataset_uri': dataset_uri,
        })

        # Submit the query
        start = time.time()
        results = self.query(query)
        runtime = round(time.time() - start, 2)

        # Log the SPARQL query
        Log.objects.create(
            type='get_dataset_label',
            sparql_query=query,
            runtime=runtime,
            result_count=len(results['results']['bindings']),
            endpoint=self.endpoint_url,
        )

        # Did we find any datasets?
        if len(results['results']['bindings']) > 0:

            # Extract the label
            result_dataset = results['results']['bindings'][0]
            dataset_label = ''
            if 'label' in result_dataset.keys():
                dataset_label = result_dataset['label']['value']
            elif 'title' in result_dataset.keys():
                dataset_label = result_dataset['title']['value']

            # Extract the description
            dataset_description = ''
            if 'description' in result_dataset.keys():
                dataset_description = result_dataset['description']['value']
            elif 'comment' in result_dataset.keys():
                dataset_description = result_dataset['comment']['value']

            # Create and save the datasets
            dataset = Dataset.objects.create(
                pk=dataset_uri,
                endpoint=Endpoint.objects.get(sparql_url=self.endpoint_url),
                label=dataset_label[:1].upper() + dataset_label[1:],
                description=dataset_description,
                size=0
            )

            return dataset

    def get_cube_dimensions(self, dataset):
        """
        Return a list with the dimensions of the given dataset.

        The list includes uri and label of each dimension.

        """
        dimensionsList = []
        query = Template("""
        PREFIX qb: <http://purl.org/linked-data/cube#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT distinct ?dimension ?component_label ?dimension_label
        WHERE {
            # GRAPH ?g {
                <$dataset> qb:structure ?structure .
                ?structure qb:component ?component .
                ?component qb:dimension ?dimension .
                OPTIONAL { ?component rdfs:label ?component_label . }
                OPTIONAL { ?dimension rdfs:label ?dimension_label . }
            # }
        }
        """).substitute({
            'dataset': dataset,
        })

        results = self.query(query)

        for component in results['results']['bindings']:
            # Get the dimension label
            if 'component_label' in component:
                label = component['component_label']['value']
            elif 'dimension_label' in component:
                label = component['dimension_label']['value']
            else:
                label = shorten_uri(component['dimension']['value'])

            # Build the dimension object
            dimensionObject = {
                'dimensionuri': component['dimension']['value'],
                'label': label,
            }
            dimensionsList.append(dimensionObject)

        return dimensionsList

    def get_cube_measure(self, dataset):
        """
        Return a list with the measures of the given dataset.

        The list includes uri and label of each measure.

        """
        # FIXME: The method name should be 'get_cube_measures'
        # FIXME: Code duplication warning (compare with 'get_cube_dimensions')

        dimensionsList = []
        query = Template("""
        PREFIX qb: <http://purl.org/linked-data/cube#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT distinct ?dimension ?component_label ?dimension_label
        WHERE {
            # GRAPH ?g {
                <$dataset> qb:structure ?structure .
                ?structure qb:component ?component .
                ?component qb:measure ?dimension .
                OPTIONAL { ?component rdfs:label ?component_label . }
                OPTIONAL { ?dimension rdfs:label ?dimension_label . }
            # }
        }
        """).substitute({
            'dataset': dataset,
        })

        results = self.query(query)

        for component in results['results']['bindings']:
            # Get the dimension label
            if 'component_label' in component:
                label = component['component_label']['value']
            elif 'dimension_label' in component:
                label = component['dimension_label']['value']
            else:
                label = shorten_uri(component['dimension']['value'])

            # Build the dimension object
            dimensionObject = {
                'measureuri': component['dimension']['value'],
                'label': label,
            }
            dimensionsList.append(dimensionObject)

        return dimensionsList

    def get_value_of_cube_measure(self, dataset, dimensions, measures,
                                  datasetFilters):
        """
        Please describe what this method does.

        Also describe what is returned and in what format.

        """
        try:
            measureContentArray = []
            dimensionString = ""

            labString = ""
            stringForSelect = ""
            labelOfString = ""
            labelForSelect = ""

            measureString = ""
            measureForSelect = ""
            num = 0

            predicateUri = ""
            type = ""
            filteredUri = ""
            numtwo = 0

            for element in dimensions:
                dimensionuri = element['dimensionuri']
                spr = "?observation  <%s> ?o%s." % (dimensionuri, num) # OPTIONAL, if transparency endpoint

                labelOfString = labelOfString + " OPTIONAL{?x%s rdfs:label ?label%s.} " % (num, num)
                stringForSelect = stringForSelect + " " + "?x%s" % (num)
                labelForSelect = labelForSelect + " " + "?label%s " % (num)
                dimensionString = dimensionString + spr
                num = num + 1

            for element in measures:
                measureForSelect = measureForSelect + " " + "?measure%s" %(numtwo)
                numtwo = numtwo + 1

            if len(datasetFilters) > 0 :
                num = 0
                for setFilter in datasetFilters:
                    filteredUri  = setFilter['value']
                    predicateUri = setFilter['predicateUri']
                    type = setFilter['type']



                    for element in dimensions:
                        dimensionuri = element['dimensionuri']
                        referenzDimUri = dimensionuri

                        labString = labString + "?observation <%s> ?x%s." % (dimensionuri, num)

                        if type == "search":
                            if referenzDimUri == predicateUri:
                                where_clause = Template(
                                    """
                                    # Worst case: Let's do a regex search
                                    FILTER regex(?x$filter_counter, '$filter_value', 'i') """
                                ).substitute({
                                    'filter_counter': num,
                                    'filter_value': filteredUri.replace('"', ''),
                                })
                                labString = labString + where_clause


                        if type == "uri":
                            if  referenzDimUri == predicateUri:
                                labString = labString + "?observation <%s> ?x%s. FILTER (?x%s =  <%s> )" % (dimensionuri, num, num, filteredUri)


                        if type == "date":

                            filteredDate = filteredUri.partition(',')
                            if filteredDate[0] and referenzDimUri == predicateUri:
                                labString = labString + "?observation <%s> ?x%s. FILTER (?x%s >= \"%s\"^^xsd:date)" % (dimensionuri, num, num, filteredDate[0])


                            if filteredDate[2] and referenzDimUri == predicateUri:
                                labString = labString + "?observation <%s> ?x%s. FILTER (?x%s <= \"%s\"^^xsd:date)" % (dimensionuri, num, num, filteredDate[2])

                        if type == "datetime":

                            filteredDate = filteredUri.partition(',')
                            if filteredDate[0] and referenzDimUri == predicateUri:
                                labString = labString + "?observation <%s> ?x%s. FILTER (?x%s >= \"%s\"^^xsd:dateTime)" % (dimensionuri, num, num, filteredDate[0])


                            if filteredDate[2] and referenzDimUri == predicateUri:
                                labString = labString + "?observation <%s> ?x%s. FILTER (?x%s <= \"%s\"^^xsd:dateTime)" % (dimensionuri, num, num, filteredDate[2])

                        num = num + 1


                        # collecting the dimensions


                    numtwo = 0
                    for element in measures:
                        measure = element['measureuri']

                        referenzDimUri = measure

                        if type == "numeric":

                            minmax = filteredUri.partition(',')

                            if  minmax[0] and referenzDimUri == predicateUri:

                                msr = "?observation <%s> ?measure%s.FILTER (?measure%s >= %s)" %(measure, numtwo, numtwo, minmax[0] )

                                measureString = measureString + msr


                            if  minmax[2] and referenzDimUri == predicateUri:
                                msr = "?observation <%s> ?measure%s.FILTER (?measure%s <= %s)" %(measure, numtwo, numtwo, minmax[2] )

                                measureString = measureString + msr


                        msr = "?observation <%s> ?measure%s." %(measure, numtwo)
                        measureString = measureString + msr


                        numtwo = numtwo + 1
            else:
                num = 0
                for element in dimensions:
                    dimensionuri = element['dimensionuri']

                    labString = labString + "?observation <%s> ?x%s." % (dimensionuri, num) # OPTIONAL, if transparency endpoint
                    num = num +1

                numtwo = 0
                for element in measures:
                    measure = element['measureuri']
                    msr = "?observation <%s> ?measure%s." %(measure, numtwo)

                    measureString = measureString + msr
                    numtwo = numtwo +1


            query = """
            PREFIX qb: <http://purl.org/linked-data/cube#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT  distinct ?observation %s %s %s
            WHERE {
            GRAPH ?g {
                ?observation rdf:type qb:Observation .
                ?observation qb:dataSet <%s> .
                %s
                %s
                %s
                %s
        }
                 } Limit 250
            """ % (labelForSelect, measureForSelect , stringForSelect, dataset, dimensionString, measureString, labString, labelOfString)

            results = self.query(query)

            for component in results['results']['bindings']:
                measureObject = {}
                measureObject['observation'] = {
                    'observation': component['observation']['value'],
                    #'measurevalue': component['measure']['value'],
                }

                for i in range(len(dimensions)):
                    if  component['x' + str(i)]['type'] == "uri":
                        measureObject['observation']['dimensionuri' + str(i)] = component['x' + str(i)]['value']
                        measureObject['observation']['dimensionlabel' + str(i)] = shorten_uri(component['x' + str(i)]['value'])
                        if component.get('label' + str(i)):
                            measureObject['observation']['dimensionlabel' + str(i)] = component['label' + str(i)]['value']
                    else:

                        measureObject['observation']['dimensionlabel' + str(i)] = component['x' + str(i)]['value']
                        #measureObject['observation']['dimensionlabel' + str(i)] = component['observation']['value']

                for i in range(len(measures)):
                    mesValue = component['measure' + str(i)]['value']
                    if not mesValue :
                        mesValue = str(0.0)

                    measureObject['observation']['measurevalue' + str(i)] = mesValue


                measureContentArray.append(measureObject)
            if len(measureContentArray) < 1:
                raise Exception("This RDF Data Cube is bad formed!")

        except Exception as ex:
            print ("-get_value_of_cube_measure: %s"%ex)
            import traceback
            print traceback.print_exc()
            raise Exception("%s"%ex)

        return measureContentArray


    def get_cube_dimensions_for_auto_mapping(self, dataset):
        try:
            """
            Please describe what this method does.
            Also describe what is returned and in what format.
            """



            testQuery = """
            PREFIX qb: <http://purl.org/linked-data/cube#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT distinct ?dimension ?component_label ?dimension_label ?datatype
            WHERE {
                GRAPH ?g {
                    <%s> qb:structure ?structure .
                    ?structure qb:component ?component .
                    ?component qb:dimension ?dimension .
                    OPTIONAL {?component rdfs:label ?component_label .}
                    OPTIONAL {?dimension rdfs:label ?dimension_label .}
                    OPTIONAL {?dimension rdfs:range ?datatype .}
                }
            }
            """ % (dataset)

            result = self.query(testQuery)

            if len (result['results']['bindings']) <1:
                    raise Exception("This dataset is either empty or the enpoint can not be accessed")

            dimensionsList = []
            query = """
            PREFIX qb: <http://purl.org/linked-data/cube#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT distinct ?dimension ?component_label ?dimension_label ?datatype
            WHERE {
                GRAPH ?g {
                    <%s> qb:structure ?structure .
                    ?structure qb:component ?component .
                    ?component qb:dimension ?dimension .
                    OPTIONAL {?component rdfs:label ?component_label .}
                    OPTIONAL {?dimension rdfs:label ?dimension_label .}
                    OPTIONAL {?dimension rdfs:range ?datatype .}
                }
            }
            """ % (dataset)

            results = self.query(query)

            datatype = "http://www.w3.org/2001/XMLSchema#string"
            for component in results['results']['bindings']:
                if component.get('datatype'):
                    datatype = component['datatype']['value']

                label = ''
                if 'component_label' in component:
                    label = component['component_label']['value']


                elif 'dimension_label' in component:
                    label = component['dimension_label']['value']

                dimensionObject = {
                    'dimensionuri': component['dimension']['value'],
                    'label': label,
                    'datatype': datatype,
                }  # wenn value schreibst, dann nimmst du den Inhalt dahinter. man kann auch den den type nehmen
                dimensionsList.append(dimensionObject)

            if len(dimensionsList) < 1:
                raise Exception("There is no dimension for this dataset")


        except Exception as ex:
            print ("-get_cube_dimensions_for_auto_mapping: %s"%ex)
            raise Exception("%s"%ex)
        
        #print "-----------------------", dimensionsList
        return dimensionsList


    def get_cube_measure_for_auto_mapping(self, dataset, deletedMeasureUri):
        try:
            """
            Please describe what this method does.
            Also describe what is returned and in what format.
            """
            measureList = []
            measureList2 = []
            query = """
            PREFIX qb: <http://purl.org/linked-data/cube#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT distinct ?dimension ?datatype ?component_label ?dimension_label
            WHERE {
                GRAPH ?g {
                    <%s> qb:structure ?structure .
                    ?structure qb:component ?component .
                    ?component qb:measure ?dimension .
                    OPTIONAL {?component rdfs:label ?component_label .}
                    OPTIONAL {?dimension rdfs:label ?dimension_label .}
                    OPTIONAL {?dimension rdfs:range ?datatype .}
                }
            }
            """ % (dataset)

            results = self.query(query)
            datatype = "http://www.w3.org/2001/XMLSchema#decimal"
            for component in results['results']['bindings']:
                # whit "value" can you get the content
                # but you can also get the "type"
                if component.get('datatype'):
                    datatype = component['datatype']['value']

                label = ''
                if 'component_label' in component:
                    label = component['component_label']['value']
                elif 'dimension_label' in component:
                    label = component['dimension_label']['value']
                if not label:
                    label = shorten_uri(component['dimension']['value'])



                if component['dimension']['value'] not in deletedMeasureUri:
                    measureObject = {'measureuri': component['dimension']['value'],'datatype': datatype, 'label': label}
                    measureList.append(measureObject)


            if len(measureList) < 1:
                raise Exception("There is no measure for this dataset")

        except Exception as ex:
            print ("-get_cube_dimensions_for_auto_mapping: %s"%ex)
            raise Exception("%s"%ex)

        return measureList

    def unique_dimensions (self, dataset, dimensions, measureContentArray):
        dimArray = []
        newArray = []

        for i in range(len(dimensions)-1):
                for elements in measureContentArray:
                    dimlab1 = elements['observation']['dimensionlabel%s'%i]
                    dimlab2 = elements['observation']['dimensionlabel%s'%(i+1)]
                    dimArray.append (dimlab1)
                    dimArray.append(dimlab2)

                    collection = collections.Counter(dimArray)
                    newArray = []
                    for key in collection:
                        value = collection[key]

                        if value <= 1:
                            newArray.append( { key : value} )

        return newArray


    def get_label_of_dimensions(self, dataset, xAxisUri ):
        try:
            dimensionsList = []
            query = """
            PREFIX qb: <http://purl.org/linked-data/cube#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT  distinct ?lab
            WHERE {
                ?observation rdf:type qb:Observation .
                ?observation qb:dataSet <%s> .
                ?observation ?p <%s>.
                ?p rdfs:label ?lab
                 }
            """ % (dataset, xAxisUri)
            results = self.query(query)

            for component in results['results']['bindings']:
                dimensionObject = {'label':component['lab']['value']}  # wenn value schreibst, dann nimmst du den Inhalt dahinter. man kann auch den den type nehmen
                dimensionsList.append(dimensionObject)

        except Exception as ex:
            raise Exception("-get_label_of_dimensions: %s"%ex)

        return dimensionsList
        pass


    def defineDate(self, init):
        min = 1900
        max = 2100
        rNumber = math.ceil(init)

        if (rNumber >= min and rNumber <=max):
            return True
        else:
            return False


    def update(self, query):
        results = self.query(query, True)
        return results



def shorten_uri(uri):
    """
    Quick hack to make URIs a little bit shorter for displaying.

    Return the shortened URI as plain text.

    """
    #Check what type of URI it is
    if "#" in uri:
        # It's a hash uri! Use the part after the last #
        shortened_uri = uri.split("#")[-1]
    else:
        # It's a slash URI! Use the part after the last /
        shortened_uri = uri.split("/")[-1]

    # Make the first letter uppercase
    shortened_uri = shortened_uri[:1].upper() + shortened_uri[1:]

    # Return our beautifully shortened URI
    return shortened_uri


def generate_inverse_label(label):
    """Generate and return the inverse label as a string."""
    if label == "Broader":
        inverse_label = "Narrower"
    else:
        inverse_label = label + ' of'

    return inverse_label
