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

import mappingproposal
import generatorfactoryforautomapping
import mappingalgorithm
from ldva.libs.sparql.utils import SPARQLQuery
from django.utils import simplejson
from ldva.libs.sparql.models import Endpoint

import time

class OutProcessorForAutomaticallyMapping():
    resultArrayForVis = []

    def __init__ (self, dataset, chart, dimension, endpoint, deletedMeasure, chartrowindex, datasetFilters):

        self.dataset = dataset
        self.selectedChart = chart
        self.dimension = dimension


        self.endpoint = endpoint
        self.deletedMeasure = deletedMeasure
        self.chartrowIndex = chartrowindex
        self.datasetFilters =  datasetFilters

        possibleVisualizations = []

    def process(self):
        try:

            chartComponentsArray = []

            mappingProposalObject=mappingproposal.MappingProposal()
            sparqlqueryObjectD3 = ""


            mappingAlgorithmlObject = mappingalgorithm.MappingAlgorithm()



            '''st = "http://data.lod2.eu/"
            if st in self.dataset:
                sparqlqueryObjectD3 = SPARQLQuery('http://open-data.europa.eu/en/sparqlep', 'regex')
            else:
                sparqlqueryObjectD3 = SPARQLQuery('http://zaire.dimis.fim.uni-passau.de:8890/sparql', 'virtuoso')'''

            if not self.endpoint:
                self.endpoint = \
                    'http://zaire.dimis.fim.uni-passau.de:8890/sparql'

            search_type = 'regex'
            time1 = time.time()
            sparqlqueryObjectD3 = SPARQLQuery(self.endpoint, search_type)

            time1_end = time.time() - time1

            time2 = time.time()
            dimensions = sparqlqueryObjectD3.get_cube_dimensions_for_auto_mapping(self.dataset)
            time2_end = time.time() - time2

            time3 = time.time()
            measure = sparqlqueryObjectD3.get_cube_measure_for_auto_mapping(self.dataset, self.deletedMeasure)
            time3_end = time.time() - time3

            time4 = time.time()
            valueOfMeasure = sparqlqueryObjectD3.get_value_of_cube_measure(self.dataset, dimensions, measure,  self.datasetFilters)
            time4_end = time.time() - time4


            time5 = time.time()
            #chartComponentsArray = mappingProposalObject.getChartComponents()
            time5_end = time.time() - time5

            time6 = time.time()

            mappingQueries = mappingProposalObject.getMappingQueries(dimensions, measure )

            time6_end = time.time() - time6

            time7 = time.time()

            possibleVisualizations = mappingProposalObject.getPossibleVisualizationVariants(mappingQueries, dimensions, measure,valueOfMeasure)

            time7_end = time.time() - time7

            '''print "TIMES: \n ------------------------------------"
            print "T1: ", time1_end
            print "T2: ", time2_end
            print "T3: ", time3_end
            print "T4: ", time4_end
            print "T5: ", time5_end
            print "T6: ", time6_end
            print "T7: ", time7_end'''


            #print "----------------possible vis------------------------------", possibleVisualizations
            return possibleVisualizations

        except Exception as ex:
            print ("-OutProcessorauto.process: %s"%ex)
            raise Exception("%s"%ex)

    def getVis(self):
        try:
            sparqlqueryObjectD3 = ""
            resultObject = {}

            '''st = "http://data.lod2.eu/"
            if st in self.dataset:
                sparqlqueryObjectD3=SPARQLQuery('http://open-data.europa.eu/en/sparqlep', 'regex')
            else:
                sparqlqueryObjectD3=SPARQLQuery('http://zaire.dimis.fim.uni-passau.de:8890/sparql', 'virtuoso')'''

            if not self.endpoint:
                self.endpoint = \
                    'http://zaire.dimis.fim.uni-passau.de:8890/sparql'

            search_type = 'regex'

            sparqlqueryObjectD3 = SPARQLQuery(self.endpoint, search_type)

            measure = sparqlqueryObjectD3.get_cube_measure_for_auto_mapping(self.dataset, self.deletedMeasure)
            valueOfMeasure=sparqlqueryObjectD3.get_value_of_cube_measure(self.dataset, self.dimension, measure,  self.datasetFilters)

            generatorFactoryObjectAuto=generatorfactoryforautomapping.GeneratorFactoryForAutoMapping()
            generatorauto=generatorFactoryObjectAuto.createFactoryauto(self.selectedChart, self.dimension, measure, valueOfMeasure, self.dataset, self.chartrowIndex  )



            if generatorauto != None:
                generatorauto.transform()
                columns = ""
                rows = ""
                if generatorauto.results.has_key("columns"):
                    columns = generatorauto.results['columns']
                if generatorauto.results.has_key("rows"):
                    rows = generatorauto.results['rows']

                resultObject = {'name':self.selectedChart,'start':generatorauto.results['code'], 'rows':rows, 'columns':columns}


                return resultObject

        except Exception as ex:
            print ("-OutProcessorauto.getVis: %s"%ex)
            raise Exception("%s"%ex)



