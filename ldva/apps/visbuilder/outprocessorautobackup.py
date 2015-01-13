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
from ldva.libs.sparql.utils import SPARQLQuery

class OutProcessorForAutomaticallyMapping():
    resultArrayForVis = []

    def __init__ (self, dataset, chart, dimension):
        self.dataset=dataset
        self.selectedChart=chart
        self.dimension = dimension

    def process(self):
        try:
            print "OutProcessorForAutomaticallyMapping::start..."
            resultArray = []
            supportedCharts = []
            supportedArray = []

            mappingProposalObject=mappingproposal.MappingProposal()
            sparqlqueryObjectD3 = ""
            print "OutProcessorForAutomaticallyMapping::1...",self.dataset
            '''if self.dataset == "http://data.lod2.eu/scoreboard/ds/indicator/i_iuolc_IND_TOTAL__ind_iu3":
                sparqlqueryObjectD3 = SPARQLQuery("http://open-data.europa.eu/en/sparqlep", 'regex')'''


            st = "http://data.lod2.eu/"
            if st in self.dataset:
                sparqlqueryObjectD3 = SPARQLQuery('http://open-data.europa.eu/en/sparqlep', 'regex')

            else:
                sparqlqueryObjectD3 = SPARQLQuery('http://zaire.dimis.fim.uni-passau.de:8890/sparql', 'virtuoso')


            dimensions = sparqlqueryObjectD3.get_cube_dimensions_for_auto_mapping(self.dataset)
            measure = sparqlqueryObjectD3.get_cube_measure_for_auto_mapping(self.dataset)


            #valueOfMeasure = sparqlqueryObjectD3.get_value_of_cube_measure(self.dataset, dimensions, measure, 10)
            chartComponentsArray = mappingProposalObject.getChartComponents()
            #print "OLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", chartComponentsArray, "DIMMMMMMMMMMMMMMMMM", dimensions
            supportedCharts = mappingProposalObject.getSupportedChart(chartComponentsArray, dimensions, measure)
            #print "JETZT: ", len(supportedCharts)
            for element in supportedCharts:
                ch = element ['chart']
                chartComponent = { 'chart':'', 'charturi':'', 'visualChannels': []}

                chUri = element ['charturi']
                chartComponent[ 'chart'] = ch
                chartComponent[ 'charturi'] = chUri

                supportedArray = mappingProposalObject.getVisChannelsOfSupportedChart(chUri, chartComponentsArray, dimensions, measure)
                chartComponent['visualChannels'] = supportedArray
                resultArray.append(chartComponent)
            #print "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT", resultArray
            return resultArray

        except Exception as ex:
            raise Exception("-OutProcessorauto.process: %s"%ex)

    def getVis(self):
        try:
            resultArrayForVis = []
            sparqlqueryObjectD3 = ""
            '''if self.dataset == "http://data.lod2.eu/scoreboard/ds/indicator/i_iuolc_IND_TOTAL__ind_iu3":
                sparqlqueryObjectD3 = SPARQLQuery("http://open-data.europa.eu/en/sparqlep", 'regex')'''


            st = "http://data.lod2.eu/"
            if st in self.dataset:
                sparqlqueryObjectD3=SPARQLQuery('http://open-data.europa.eu/en/sparqlep', 'regex')
            else:
                sparqlqueryObjectD3=SPARQLQuery('http://zaire.dimis.fim.uni-passau.de:8890/sparql', 'virtuoso')
            #dimensions=sparqlqueryObjectD3.get_cube_dimensions_for_auto_mapping(self.dataset)
            measure = sparqlqueryObjectD3.get_cube_measure_for_auto_mapping(self.dataset)

            #valueOfMeasure=sparqlqueryObjectD3.get_value_of_cube_measure(self.dataset, dimensions, measure, 10)
            valueOfMeasure=sparqlqueryObjectD3.get_value_of_cube_measure(self.dataset, self.dimension, measure, 150)


            generatorFactoryObjectAuto=generatorfactoryforautomapping.GeneratorFactoryForAutoMapping()
            generatorauto=generatorFactoryObjectAuto.createFactoryauto(self.selectedChart, self.dimension, measure, valueOfMeasure, self.dataset )

            if generatorauto != None:
                generatorauto.transform()

                transformedResult=generatorauto.results

                resultObject = {'name':self.selectedChart,'start':transformedResult['code']}
                transformedResult=generatorauto.results;


                resultArrayForVis.append(resultObject)
                #print "ID###########################", resultArrayForVis
                return resultArrayForVis
        except Exception as ex:
                raise Exception("-OutProcessorauto.getVis: %s"%ex)
