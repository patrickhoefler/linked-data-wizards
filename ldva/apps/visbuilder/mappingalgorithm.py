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

import os
import rdflib
import time
import random 

from datetime import datetime


class MappingAlgorithm():    
    ''' Algorithm for automated mapping proposal
        Main steps:
        1. find matching charts and make possible combinations with provided dimensions and measure
        2. check whether some of the combinations consist of visual channels which are instantiated more than once
        3. check whether some of the channels are missing
        4. filter proposed list and provide only valid combinations
    '''

   

    def getPossibleVisualizationVariants(self, dimensions, measure, valueOfMeasure):
        vcArray = self.readChartRdf(dimensions, measure)
        newFilteredChart = self.findVisualChannels (dimensions, measure, vcArray)
        self.suggestChartPhase1(dimensions, measure, newFilteredChart)
      
    
    
    
    
    def readChartRdf (self, dimensions, measure):
        try:
            gChart=rdflib.Graph()
            gChart.load(os.path.join(os.path.dirname(__file__), 'static/data/chart.rdf'))
             
            fileredCharts = self.filteringOfTheCharts(gChart, dimensions, measure) 
             
                
            sQ="""
                prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                prefix va: <http://code-research.eu/ontology/visual-analytics#>
                
                SELECT distinct ?s ?nameofchart  
                WHERE { 
                    ?s rdfs:label ?nameofchart.
                    %s
                    ?s va:hasChartName ?chartNameUri                    
                }
                """ %(fileredCharts )
                
            vcArray = []
            
            for xQ in gChart.query( sQ ):
                chartURI = xQ[0]
                chartName = xQ[1] 
            
                sQQ="""
                    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                    prefix va: <http://code-research.eu/ontology/visual-analytics#>
                    
                    SELECT distinct ?s ?visualChannel ?vcName ?vcDatatype ?vcOccurrence ?vcPersistence  
                    WHERE { 
                        ?s rdfs:label "%s".                    
                        ?s va:hasVisualChannel ?visualChannel.                           
                        ?visualChannel va:hasDataType ?vcDatatype.
                        ?visualChannel rdfs:label ?vcName.
                        ?visualChannel va:hasPersistence ?vcPersistence.
                        ?visualChannel va:hasOccurrence ?vcOccurrence 
                    }
                    """ %( chartName )
                    
                chartBundle = { 'chartURI' : str(chartURI), 'chartName' : str(chartName), 'visualChannels' : [] }
                
                #print "CHART: ", chartBundle, "\n", sQQ
                for xQQ in gChart.query( sQQ ):
                    
                    visualChannel = xQQ[1] 
                    vcName = xQQ[2]
                    vcDatatype = xQQ[3]
                    vcOccurrence = xQQ[4]
                    vcPersistence= xQQ[5]
        
                    vcEntry = { 'visualChannelURI' : str(visualChannel), 
                             'vcName' : str(vcName),
                             'vcDatatypes' : [ str(vcDatatype) ], 
                             'vcOccurrence' : str(vcOccurrence), 
                             'vcPersistence' : str(vcPersistence) }
                
                    vcFound = 0
                    for vc in chartBundle['visualChannels']: 
                        if vc['vcName'] == str(vcName):
                            vc['vcDatatypes'].append( str(vcDatatype) )
                            vcFound = 1
                    
                    # if the visual channel is not in the list, then add it
                    if vcFound == 0:
                        chartBundle['visualChannels'].append(vcEntry)
                    
           
                    vcArray.append(chartBundle) 
                    vcArray = self.unique(vcArray)
            
            
                
            return vcArray    
           
        except Exception as ex:
            raise Exception("-Mappingalgorithm.readChartRdf: %s"%ex)       
                
            
            
    def filteringOfTheCharts(self, gChart, dimensions, measure):
        try:
            dimensionLength = len(dimensions)
            measureLength = len(measure)
                

            strFilter = "?s va:supportedDimension ?supportedDims. FILTER (?supportedDims = " + str(dimensionLength) + " ||?supportedDims = "+ str( 9999)+" )"    
            strFilter2 = "?s va:supportedMeasure ?supportedMes. FILTER (?supportedMes = " + str(measureLength) + " ||?supportedMes = "+ str( 9999)+" )" 
            firstCandidates = []
            
            s1="""
                prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                prefix va: <http://code-research.eu/ontology/visual-analytics#>
                
                SELECT distinct ?name 
                WHERE {                
                        %s
                        %s
                        ?s rdfs:label ?name
                }  
            
            """ %(strFilter, strFilter2)
            
            
            strFilter2 = "?s va:supportedDimensionalt ?supportedDims. FILTER (?supportedDims = " + str(dimensionLength) + " ||?supportedDims = "+ str( 9999)+" )"    
            strFilter22 = "?s va:supportedMeasurealt ?supportedMes. FILTER (?supportedMes = " + str(measureLength) + " ||?supportedMes = "+ str( 9999)+" )" 
            
            
            
            # When a chart has two options for the supporting measures and dimensions, this sparql query gets also this chart.
            
            
            s2="""
                prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                prefix va: <http://code-research.eu/ontology/visual-analytics#>
                
                SELECT distinct ?name 
                WHERE {                 
                        %s
                        %s
                        ?s rdfs:label ?name
                }  
            
            """ %(strFilter2, strFilter22)
        
            filteredCharts = gChart.query(s1)      
            strChartPart = " FILTER ( "
            
            filteredChartsList = []
            for fChart in filteredCharts:
                firstCandidates.append(fChart[0])           
                filteredChartsList.append("?nameofchart = '" + fChart[0] + "'")
                 
            filteredCharts2 = gChart.query(s2)                  
            filteredChartsList2 = []
            for fChart in filteredCharts2:
                firstCandidates.append(fChart[0])           
                filteredChartsList2.append("?nameofchart = '" + fChart[0] + "'")               
                  
            newfilteredChartsList = []
            for element in  filteredChartsList:
                newfilteredChartsList.append(element)
            
            for el in filteredChartsList2:
                newfilteredChartsList.append(el)                
                
            #print newfilteredChartsList
            strChartPart += " || ".join(newfilteredChartsList)               
            strChartPart += " ) ."
             
            
            
            #print "*************************", strChartPart
            return strChartPart
        except Exception as ex:
            raise Exception("-Mappingalgorithm.filteringOfTheCharts: %s"%ex)      
            

    def unique(self, items):
        found = []
        keep = []
    
        for item in items:
            if item not in found:
                found.append(item)
                keep.append(item)
    
        return keep 



    def findVisualChannels (self, dimensionList, measureList, filteredCharts):
        try:
            numRequiredVisualChannels = len(dimensionList) + len(measureList)
                
            for chart in filteredCharts:
                vcList = chart['visualChannels']
                
                #now, we have to look how many visual channels we need to instantiate for charts with higher cardinality
                numOptionalVisualChannelsToInsantiate = numRequiredVisualChannels - len( vcList )
                if ( numOptionalVisualChannelsToInsantiate > 0):
                    for vc in vcList:
                        vcOccurrence = vc['vcOccurrence']
                        
                        # if we have occurrence multiplicity - then we to make numOptionalVisualChannelsToInstantiate instances
                        if ( vcOccurrence == 'http://code-research.eu/ontology/visual-analytics#Multiplicity' ):
                            for instance in range(0, numOptionalVisualChannelsToInsantiate):
                                vcList.append( vc )
                                instance
                            break;          
            return filteredCharts
        except Exception as ex:
            raise Exception("-Mappingalgorithm.readDatatypesOfCubeComponents: %s"%ex)    
        
        

    def suggestChartPhase1(self, dimesions, measures, newfilteredCharts):
       
        cubeComponents = []          
        validCombinations = []
        
        for dimension in dimesions:
            cubeComponents.append(dimension)  
           
        for measure in measures:
            cubeComponents.append(measure)
            
        for chart in newfilteredCharts:
                vcList = chart['visualChannels']
                
                combinedList = [vcList, cubeComponents]
                

    def millis(self, start_time):
        dt = datetime.now() - start_time
        ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
        return ms

    def random_product(self, *args, **kwds):
        pools = map(tuple, args) * kwds.get('repeat', 1)
        return tuple(random.choice(pool) for pool in pools)
    
    '''Datatype compatibility - checks whether two arrays (charts, cube) are compatible regarding their datatypes'''
    def isTypeCompatible(self, combinationList ):
        try:
            entryIndex = 0
            
            cubeComponent = { 'datatype' : '' }
            visualChannel = { 'vcDatatypes' : [] }
            
            
            
            for combinationEntry in combinationList:
                if ((  entryIndex % 2 ) == 0 ):
                    visualChannel = combinationEntry
                else:
                    cubeComponent = combinationEntry
                    if ( cubeComponent['datatype'] not in visualChannel['vcDatatypes'] ):
                        return 0
                entryIndex = entryIndex + 1
            
            return 1
        except Exception as ex:
            raise Exception("-Mapping.isTypeCompatible: %s"%ex)