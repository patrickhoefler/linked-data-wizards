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
import generatorfactory
from ldva.libs.sparql.utils import SPARQLQuery

class OutProcessor():
    selectedChart=""
    resultArray=[]
    
    def __init__ (self, dataset, chart, chartID):
        self.dataset=dataset
        self.selectedChart=chart  
        self.IDofSelectedChart=chartID 
        
        
    def process(self):
        try:
            self.resultArray = []
            mappingProposalObject=mappingproposal.MappingProposal()
            limitForGoogle=10
            limitForStreamgraph=400
            limitForD3=100
            limitForGroupedBarChart=100
            
            #self.dataset="http://code-research.eu/resource/datasetpan_2009_ext"
            if not self.dataset:
        
                if self.IDofSelectedChart=="google" or self.IDofSelectedChart=="googleFull":
                    sparqlqueryObject=SPARQLQuery("http://open-data.europa.eu/en/sparqlep", 'regex')
                    dimensions=sparqlqueryObject.get_cube_dimensions("http://data.lod2.eu/scoreboard/ds/indicator/i_iuolc_IND_TOTAL__ind_iu3")
                    

                    measure = sparqlqueryObject.get_cube_measure("http://data.lod2.eu/scoreboard/ds/indicator/i_iuolc_IND_TOTAL__ind_iu3")
                    limit = limitForGoogle
                    if self.IDofSelectedChart=="googleFull":
                        limit = 1000
                    valueOfMeasure=sparqlqueryObject.get_value_of_cube_measure("http://data.lod2.eu/scoreboard/ds/indicator/i_iuolc_IND_TOTAL__ind_iu3", dimensions, measure, limit)
                    
                if self.IDofSelectedChart=="d3":
                    sparqlqueryObjectD3=SPARQLQuery('http://zaire.dimis.fim.uni-passau.de:8890/sparql', 'virtuoso')
            
                    dimensions=sparqlqueryObjectD3.get_cube_dimensions("http://code-research.eu/resource/datasetpan_2009_ext")
                    measure = sparqlqueryObjectD3.get_cube_measure("http://code-research.eu/resource/datasetpan_2009_ext")
                    valueOfMeasure=sparqlqueryObjectD3.get_value_of_cube_measure("http://code-research.eu/resource/datasetpan_2009_ext", dimensions, measure, limitForD3)
                    
                if self.IDofSelectedChart=="streamgraph":
                    sparqlqueryObject=SPARQLQuery("http://open-data.europa.eu/en/sparqlep", 'regex')
                    dimensions=sparqlqueryObject.get_cube_dimensions("http://data.lod2.eu/scoreboard/ds/indicator/i_iuolc_IND_TOTAL__ind_iu3")
                    
                    measure = sparqlqueryObject.get_cube_measure("http://data.lod2.eu/scoreboard/ds/indicator/i_iuolc_IND_TOTAL__ind_iu3")
                    valueOfMeasure=sparqlqueryObject.get_value_of_cube_measure("http://data.lod2.eu/scoreboard/ds/indicator/i_iuolc_IND_TOTAL__ind_iu3", dimensions, measure, limitForStreamgraph)
                 
                 
                if self.IDofSelectedChart=="grouped":
                    sparqlqueryObject=SPARQLQuery("http://open-data.europa.eu/en/sparqlep", 'regex')
                    dimensions=sparqlqueryObject.get_cube_dimensions("http://data.lod2.eu/scoreboard/ds/indicator/i_iuolc_IND_TOTAL__ind_iu3")
                    
                    measure = sparqlqueryObject.get_cube_measure("http://data.lod2.eu/scoreboard/ds/indicator/i_iuolc_IND_TOTAL__ind_iu3")
                    valueOfMeasure=sparqlqueryObject.get_value_of_cube_measure("http://data.lod2.eu/scoreboard/ds/indicator/i_iuolc_IND_TOTAL__ind_iu3", dimensions, measure, limitForGroupedBarChart)
                     
            else:
                if self.IDofSelectedChart=="google" or self.IDofSelectedChart=="googleFull":
                    sparqlqueryObject=SPARQLQuery("http://open-data.europa.eu/en/sparqlep", 'regex')
                    dimensions=sparqlqueryObject.get_cube_dimensions(self.dataset)

                    measure = sparqlqueryObject.get_cube_measure(self.dataset)
                    limit = limitForGoogle
                    if self.IDofSelectedChart=="googleFull":
                        limit = 1000
                    valueOfMeasure=sparqlqueryObject.get_value_of_cube_measure(self.dataset, dimensions, measure, limit)
                    
                if self.IDofSelectedChart=="d3":
                    sparqlqueryObjectD3=SPARQLQuery('http://zaire.dimis.fim.uni-passau.de:8890/sparql', 'virtuoso')
            
                    dimensions=sparqlqueryObjectD3.get_cube_dimensions(self.dataset)
                    measure = sparqlqueryObjectD3.get_cube_measure(self.dataset)
                    valueOfMeasure=sparqlqueryObjectD3.get_value_of_cube_measure(self.dataset, dimensions, measure, limitForD3)
                    
                if self.IDofSelectedChart=="streamgraph":
                    sparqlqueryObject=SPARQLQuery("http://open-data.europa.eu/en/sparqlep", 'regex')
                    dimensions=sparqlqueryObject.get_cube_dimensions(self.dataset)
                    
                    measure = sparqlqueryObject.get_cube_measure(self.dataset)
                    valueOfMeasure=sparqlqueryObject.get_value_of_cube_measure(self.dataset, dimensions, measure, limitForStreamgraph)
                 
                 
                if self.IDofSelectedChart=="grouped":
                    sparqlqueryObject=SPARQLQuery("http://open-data.europa.eu/en/sparqlep", 'regex')
                    dimensions=sparqlqueryObject.get_cube_dimensions(self.dataset)
                    
                    measure = sparqlqueryObject.get_cube_measure(self.dataset)
                    valueOfMeasure=sparqlqueryObject.get_value_of_cube_measure(self.dataset, dimensions, measure, limitForGroupedBarChart)         
             
             
            mappingProposalObject.getChartComponents()
            firstPhaseMapping = mappingProposalObject.getFirstPhaseMapping()
            firstPhaseMappingForMeasure = mappingProposalObject.getFirstPhaseMappingForMeasure()
            
            generatorFactoryObject=generatorfactory.GeneratorFactory()
            generator=generatorFactoryObject.createFactory(self.selectedChart, dimensions, measure, valueOfMeasure)
            print "HERE I AM", dimensions
            if generator != None:
                generator.transform()
                
                transformedResult=generator.results
                columns = ""
                rows = ""
                if transformedResult.has_key("columns"):
                    columns = transformedResult['columns']
                if transformedResult.has_key("rows"):
                    rows = transformedResult['rows']

                resultObject = {'name':self.selectedChart,'start':transformedResult['code'],  'rows':rows, 'columns':columns}

                transformedResult=generator.results;
                #print "ID###########################", resultObject

                self.resultArray.append(resultObject)
        except Exception as ex:
            raise Exception("-OutProcessor.process: %s"%ex)
            
            
            
            
 