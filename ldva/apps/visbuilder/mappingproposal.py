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


class MappingProposal():    
    ''' Algorithm for automated mapping proposal
        Main steps:
        1. find matching charts and make possible combinations with provided dimensions and measure
        2. check whether some of the combinations consist of visual channels which are instantiated more than once
        3. check whether some of the channels are missing
        4. filter proposed list and provide only valid combinations
    '''
    '''
    Build SPARQL Queries for the Mapping-Algorithm
    '''
    def getMappingQueries(self, dimension, measure):    
        try: 
            time1 = time.time()
            strSelectPart = ""
            strWhereHasVisualChannel = ""
            
            strWhereLabel = ""
            strWhereHasDatatype = ""
            strWhereFilter = ""        
            
            collectedDimensionLabels = []        
            dimensionLength = len(dimension)
            measureLength = len(measure)
            
            sparqlArray = []
            num = 0
            num2 = 1
            
            i = 0         
            for entry in dimension:
                strSelectPart = strSelectPart + "?dimVis" + str(num) + " "
                strWhereHasVisualChannel = strWhereHasVisualChannel + "?s va:hasVisualChannel ?dimVis" + str(num) + ". \n"
      
                strWhereLabel = strWhereLabel + "?dimVis"+ str(num) +" rdfs:label ?dimensionVar"+ str(num) +". \n"
                dimDataType = entry['datatype']
                
                strWhereHasDatatype = strWhereHasDatatype + "?dimVis" + str(num)+" va:hasDataType <"+dimDataType+">. \n"           
                collectedDimensionLabels.append("?dimVis" + str(num))
                
                sparqlObject = {'strSelectPart':strSelectPart, 'strWhereLabel':strWhereLabel, 'strWhereHasDatatype':strWhereHasDatatype, 'strWhereHasVisualChannel':strWhereHasVisualChannel,  }           
                remainder = num2%30
                
                i = i + 1           
                if remainder == 0 or (num2 == len(dimension)):
                    sparqlObject['i'] = i
                    sparqlArray.append(sparqlObject)
                    strSelectPart = ""
                    
                    strWhereHasVisualChannel = ""
                    strWhereLabel = ""
                    strWhereHasDatatype = ""
                    i = 0
                    
                num = num + 1
                num2 = num2 + 1
    
            strSelectPartMeasure = ""
            strWhereHasVisualChannelMeasure = ""
            
            strWhereLabelMeasure = ""
            strWhereHasDatatypeMeasure = ""
            num = 1  
            imeasure = 0 
            for entry in measure:
                strSelectPartMeasure = strSelectPartMeasure + "?measureVis" + str(num) + " "
                strWhereHasVisualChannelMeasure = strWhereHasVisualChannelMeasure + "?s va:hasVisualChannel ?measureVis" + str(num) + ". \n"
     
                strWhereLabelMeasure = strWhereLabelMeasure + "?measureVis"+ str(num) +" rdfs:label ?measureVar"+ str(num) +". \n"
    
                measureDataType = entry['datatype']
                strWhereHasDatatypeMeasure = strWhereHasDatatypeMeasure + "?measureVis" + str(num)+" va:hasDataType <"+measureDataType+">. \n"
                
                collectedDimensionLabels.append("?measureVis" + str(num))
                num = num + 1
                imeasure =imeasure +1 
                
            time1_end = time.time() - time1
            time2 = time.time()
            
            time2_end = time.time() - time2
            time3 = time.time() 
                  
            gChart=rdflib.Graph()
            gChart.load(os.path.join(os.path.dirname(__file__), 'static/data/chart.rdf'))
            #gChart.load('http://codev.know-center.tugraz.at/static/data/chart.rdf')
            #gChart.load('http://localhost:8000/static/data/chart.rdf')
            time3_end = time.time() - time3
            time4 = time.time()
            
            
            strChartPart = self.filteringOfTheCharts(gChart, dimension, measure)
            #print "--------FILTERRFRRRR------------", strChartPart
            counter = 0
            mappingQueries = []       
            for sparql in sparqlArray:
                strSelectPart = sparql['strSelectPart'] + " " +  strSelectPartMeasure
                strWhereLabel = sparql['strWhereLabel'] + " " + strWhereLabelMeasure
                
                strWhereHasDatatype = sparql['strWhereHasDatatype'] + " " + strWhereHasDatatypeMeasure
                strWhereHasVisualChannel = sparql['strWhereHasVisualChannel'] + " " + strWhereHasVisualChannelMeasure
                
                counter = counter + 1 
                i = sparql['i']
                s="""
                    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                    prefix va: <http://code-research.eu/ontology/visual-analytics#>
                    
                    SELECT distinct ?s ?nameofchart %s 
                    WHERE { 
                            ?s rdfs:label ?nameofchart.                    
                            %s                           
                            %s                            
                            %s 
                            %s                                                                       
                    }
                
                """ %(strSelectPart, strChartPart, strWhereHasVisualChannel, strWhereLabel, strWhereHasDatatype)
                
                #print s
                strSelectPartMeasure = ""
                strWhereLabelMeasure = ""
                
                strWhereHasDatatypeMeasure = ""
                strWhereHasVisualChannelMeasure = ""
                           
                numParameters = i
                if counter == 1:
                    numParameters = i+imeasure # instead 1 measure
                else:
                    numParameters = i
                
                mappingQueryObject = {'query':s, 'parameters':numParameters }
                mappingQueries.append (mappingQueryObject)
            
            
            #print mappingQueries    
            return mappingQueries

        except Exception as ex:
            raise Exception("-Mapping.getMappingQueries: %s"%ex) 
    

    

    '''Algortihm to find out all mapping variations'''
    def getPossibleVisualizationVariants(self, mappingQueries, dimension, measure, values): 
        try:
            supportedCharts = [] 
            gChart=rdflib.Graph()
            time1 = time.time()
            
            gChart.load(os.path.join(os.path.dirname(__file__), 'static/data/chart.rdf'))
            #gChart.load('http://codev.know-center.tugraz.at/static/data/chart.rdf')
            #gChart.load('http://localhost:8000/static/data/chart.rdf') 
            allCombinations = []
            num = 0
           
            index = 0
            start = 0
            
            lengthOfComponents = len(dimension) + len(measure)
            
    
            elementForStream = ""
            if lengthOfComponents <= 3:
                
                # Each query of the mappingqueris will be execute separately
                for query in mappingQueries:
                    num = num + 1
                    allPartCombinations = [] #TODO: info, beside name (mappedTo), so it will be clear what the proposal shows             
                    start = index * 5
 
                    for x in gChart.query(query['query']):   
                        #print x, '\n'               
                        chart={ 'charturi':x[0], 'chartname':x[1]}                                 
                        chart['visualchannels'] = []
                        for cnt in range(query['parameters']): 
                            #print "range(query['parameters'])", range(query['parameters']), 'cnt', cnt
                            visualChannel = { 'name' : '' }
                            visualChannel['name'] = x[cnt+2]                    
                            targetChannel = ""
                            if index == 0:
                                if cnt <= query['parameters']-len(measure)- 1:
                                   #print cnt 
                                    targetChannel = dimension[start+cnt]
                                else:
                                    targetChannel = measure[query['parameters']-cnt-1]

                            else:
                                targetChannel = dimension[start+cnt]
                                          
                            p="""
                                prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                                prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                                prefix va: <http://code-research.eu/ontology/visual-analytics#>
                            
                                SELECT distinct  ?lab 
                                WHERE {                                                              
                                        <%s> rdfs:label ?lab.                
                                      }
                            
                                """%(x[cnt+2])
                            #print p
                            for y in gChart.query(p):            
                                visualChannel['label'] = y[0]
                                visualChannel['charturi'] = x[0]
                                
                                visualChannel['chartname'] = x[1]
                                #print 'targetchannel', targetChannel
                                visualChannel['component'] = targetChannel
                                      
                                chart['visualchannels'].append(visualChannel)
                        allPartCombinations.append(chart)    
                        
                    #print "allcombiiiiii", allPartCombinations
                    allPartCombinations = self.unique(allPartCombinations)
                    #print "allcombiiiiii", allPartCombinations
                    combinationObject = { 'part': num, 'combinations':allPartCombinations }
                    
                    allCombinations.append(combinationObject) 
                    index = index + 1    
                allCombinations = self.unique(allCombinations)
                if len(allCombinations) < 0:
                    raise Exception ("There is no visualization(s) for this dataset")
                # The combinations will be merged now             
                firstList = allCombinations.pop( 0 ) # The first part will be taken
                while ( len(allCombinations) > 0 ):
                    xy = allCombinations.pop( 0 ) # if there is a part 2, 3 etc. they will be one after another taken
                    
                    combinations = xy['combinations']         
                    for x in combinations:
                        existingChart = self.getChartByName(x['chartname'], firstList['combinations']) #Takes the object of a chart in firstList, which is the same like in part 2, 3 etc.
                        if existingChart:
                            chart = existingChart
                            for cnt in x['visualchannels']:
                                chart['visualchannels'].append(cnt) # Puts the visualchannels of the chart in part 2, 3 etc. in to visualchannels of the corresponding chart in part 1.
                    
                mergedCombinations = firstList['combinations']
                
                labelOfYear = self.defineDate(dimension, values)
                
                labelOfYear = self.unique(labelOfYear)    
                labelOfCountry = self.defineCountry(dimension, values)
               
                time1_end = time.time() - time1       
                time2 = time.time()
        
        
                #Now, allCombinations will be verified to extract only the valid candidates
                for entry1 in mergedCombinations:
                  
                    chartUri = entry1['charturi']
                    visualChannels = entry1['visualchannels']
                    
                    isChartCandidate = 1
                    for entry2 in visualChannels:
                        visualChannelUri = entry2['name']
                        if ( self.isChannelDuplicable(chartUri, visualChannelUri, gChart) == 0 ):
                            if ( self.isChannelDuplicated(visualChannelUri, visualChannels) == 1 ):
                                isChartCandidate = 0
                             
                    if ( isChartCandidate == 1 ):
                        if ( self.isChannelMissing( chartUri, visualChannelUri, visualChannels, gChart ) == 0 ):
                            #Hardcoded, will be removed, when we receive the datatype "date"
                            if len(labelOfYear) > 2:                           
                                    supportedCharts.append( entry1 )
                            else:
                                if entry1['chartname'] != "streamgraph":
                                       
                                        supportedCharts.append( entry1 ) 
                        
                                             
                time2_end = time.time() - time2
                
                
                supportedVisualizations = []
                for element in supportedCharts:  
                    if len(labelOfCountry) == 0:
                        if element['chartname']!="map":
                            supportedVisualizations.append(element)
                     
                    else:
                        if element['chartname']=="streamgraph":
                            visChn =  element['visualchannels'] 
                            for labels in visChn:
                                print "\n", "\n", "labels['component']['label']", labels['component']['label']
                                if labels['component']['label'] == 'Year' and  labels['label'] == 'x-Axis':
                                    elementForStream = element   
                                    supportedVisualizations.append(elementForStream)
                                        
                        else:    
                            supportedVisualizations.append(element) 
                            
                
               
               

             
                return supportedVisualizations
        
            
            elif lengthOfComponents == 4:
                #print "trueeeeeeeeeeeeeeeeeeeeeeeeeeejaaaaaaaaaaaaaaaaaaaa"
                filteredChartArray4= self.macheAnders(gChart, dimension, measure)
                return filteredChartArray4
            
            elif lengthOfComponents > 4: 
                vcArray = self.readChartRdf(gChart, dimension, measure)
                newFilteredChart = self.findVisualChannels (dimension, measure, vcArray)
                validCombinations =  self.suggestChartPhase1(dimension, measure, newFilteredChart)
                if len(validCombinations) < 1:
                    raise Exception("The dataypes of the cube components are unknown!")
                filteredChartArray4 = self.suggestChartsPhase4(validCombinations)
                return filteredChartArray4

        except Exception as ex:
            print ("-Mappingproposal.getPossibleVisualizationVariants: %s"%ex)
            raise Exception("%s"%ex)
        




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
             
            
            
            #print "*************************", s2
            return strChartPart
        except Exception as ex:
            raise Exception("-Mappingalgorithm.filteringOfTheCharts: %s"%ex)   





        
 
    def getChartByName(self, chartName, resultList):
        try:
            for element in resultList:
                chName = element['chartname']
                if chartName == chName:
                    return element
                
            return None
        except Exception as ex:
            raise Exception("-Mappingproposal.getChartByName: %s"%ex)
 
        
        
        
    '''Checks if occurence of a visual channel is one or more '''      
    def isChannelDuplicable (self, chartUri, visualChannelUri, gChart ):
        try:
            ret = 0
            time1 = time.time() 
            s="""
                prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                prefix va: <http://code-research.eu/ontology/visual-analytics#>
            
                SELECT distinct ?occurence
                WHERE { 
                        <%s> va:hasOccurrence ?occurence.
                      }
            
                """%(visualChannelUri)
           
            for x in gChart.query(s):
                if ( str(x[0]) == 'http://code-research.eu/ontology/visual-analytics#One'):
                    ret = 0
                else:
                    ret = 1
                break
            
            time1_end = time.time() - time1
            return ret
        except Exception as ex:
            raise Exception("-Mappingproposal.isChannelDuplicable: %s"%ex)
        
    '''Checks whether a visual channel is instantiated more than once'''
    def isChannelDuplicated(self, visualChannelUri, channelArray):
        try:
            ret = 0
            time1 =  time.time()
            
            numOccurences = 0
            
            for entry in channelArray:
                currentChannelUri = entry['name']
                if ( str(visualChannelUri) == str(currentChannelUri)):
                    numOccurences = numOccurences + 1
            
            if ( numOccurences > 1 ):
                ret = 1
            else:
                ret = 0
                
            time1_end = time.time() - time1
            return ret
        except Exception as ex:
            raise Exception("-Mappingproposal.isChannelDuplicated: %s"%ex)
        
        
    '''check whether some mandatory visual channels are missing in the array'''
    def isChannelMissing(self, chartUri, visualChannelUri, channelArray, gChart ):
        try:
            time1 = time.time()       
            p="""
                prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                prefix va: <http://code-research.eu/ontology/visual-analytics#>
            
                SELECT distinct ?vis ?visLabel ?visType 
                WHERE { 
                        <%s> rdfs:label ?nameofchart.
                        <%s> va:hasVisualChannel ?vis.
                        ?vis rdfs:label ?visLabel.
                        ?vis va:hasDataType ?visType.
                        ?vis va:hasPersistence <http://code-research.eu/ontology/visual-analytics#Mandatory>.
                        
                      }
            
                """%(chartUri, chartUri)
                
            for y in gChart.query(p):
                currentChannelUri = y[0]   
                     
                currentChannelExists = 0
                for entry in channelArray:
                    currentChannelSuggestedUri = entry['name']              
                    if( str(currentChannelSuggestedUri) == str(currentChannelUri) ):
                        currentChannelExists = 1
    
                if (currentChannelExists==0):
                    time1_end = time.time() - time1
                    return 1
                
            time1_end = time.time() - time1       
            return 0
        except Exception as ex:
            raise Exception("-Mappingproposal.isChannelMissing: %s"%ex)
      
      
      
    def unique(self, items):
        found = []
        keep = []
    
        for item in items:
            if item not in found:
                found.append(item)
                keep.append(item)
    
        return keep 
    
    
    ''' To define whether a dimension content is date or not '''  
    def defineDate (self, dimension, values):
        try:
            minx = 1900
            maxx = 2100
            labelArray = []
            
            for i in range(len(dimension)-1):
                for element in values:
                    label = element['observation']['dimensionlabel%s'%i]  
                    if label.isdigit():
                        if ( int(label) >= minx and int(label) <= maxx):
                            labelObject = {'label':label, 'index':i}
                            labelArray.append(labelObject)
                      
            return labelArray 
        
        except Exception as ex:
            raise Exception("-Mappingproposal.defineDate: %s"%ex)
    
    
    ''' To define whether a dimension content represents country or not. Important for Geovis (Map) '''  
    def defineCountry (self, dimension, values):
        labelOfCountryArray = []
        for element in dimension:
            labelOfDimension = element['label']
            if labelOfDimension == "Country":
                labelOfCountryArray.append(labelOfDimension)
                break
       
        return labelOfCountryArray  
    
    
    def macheAnders(self, gChart, dimensionList, measureList):
        try:
                
            vcArray = self.readChartRdf(gChart, dimensionList, measureList)    
                
            filteredChartArray1 = self.suggestChartsPhase1(dimensionList, measureList, vcArray)
            
            filteredChartArray2 = self.suggestChartsPhase2(dimensionList, measureList, filteredChartArray1)
            
            filteredChartArray3 = self.suggestChartsPhase3(dimensionList, measureList, filteredChartArray2)
            
            filteredChartArray4 = self.suggestChartsPhase4(filteredChartArray3)

            #print vcArray
            #print filteredChartArray1
            #print filteredChartArray2
            #print filteredChartArray3
            #print filteredChartArray4
            return filteredChartArray4
        except Exception as ex:
            raise Exception("-Mapping.macheAnders: %s"%ex)   
                            
    
    
    def readChartRdf (self, gChart, dimensions, measure):
        try:
            
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
                
  
    '''Just format the output to avoid changes on the client'''    
    def suggestChartsPhase4(self, combinationList):
        try:
            #print combinationList
            formattedCombinationList = []
            
            for combination in combinationList:
                chartName = combination['chartName']
                chartURI = combination['chartURI']
                
                chartCombinationList = combination['combinations']
                
                for chartCombinations in chartCombinationList:
                
                    chartEntry = {'chartname' : chartName, 'charturi' : chartURI, 'visualchannels' : []}
                        
                    for vcCombinationList in chartCombinations:
                        
                        for vcCombination in vcCombinationList:
                            cube = vcCombination['cube']
                            visualChannel = vcCombination['chart']
                            
                            vcEntry = { 'name' : visualChannel['visualChannelURI'], 
                                       'label' : visualChannel['vcName'],
                                       'chartname' : chartName,
                                       'charturi' : chartURI,
                                       'component' : cube }
                            
                            chartEntry['visualchannels'].append(vcEntry)
                            
                        
                    formattedCombinationList.append(chartEntry)
                       
            return formattedCombinationList
        except Exception as ex:
            raise Exception("-Mapping.suggestChartsPhase4: %s"%ex)
        
    def millis(self, start_time):
        dt = datetime.now() - start_time
        ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
        return ms
    
    
    '''Combinatorial function - returns a random entry within a set of cartesian product between charts and cubes'''    
    def random_product(self, *args, **kwds):
        pools = map(tuple, args) * kwds.get('repeat', 1)
        return tuple(random.choice(pool) for pool in pools)                          
                            
     
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

    '''Structure compatibility - checks whether two arrays (charts, cube) are compatible regarding their structure'''
    def isStructureCompatible(self, componentList, visualChannelList, combinationList):
        try:
            # to check:
            #1 - some visual channels are repeated because of cartesian product
            #2 - some of cubes are repeated from the same reason
            #3 - some of visual channels are instantiated and have an occurrence of one
            
            # 1 and 2: if some of them are repeated - it implies that others are missing
            for cubeComponent, visualChannel in zip(componentList, visualChannelList):
                if ( cubeComponent not in combinationList ):
                    return 0
                
                if ( visualChannel not in combinationList ):
                    return 0
                
            # 3: a) check whether some channels with the occurrence one are instantiated more than once; b) check the same for cube components
            # 3a)
            vcMandatoryList = []
            entryIndex = 0
            for combinationEntry in combinationList:
                if ((  entryIndex % 2 ) == 0 ):
                    visualChannel = combinationEntry
                    vcOccurrence = visualChannel['vcOccurrence']
                        
                    if ( vcOccurrence != 'http://code-research.eu/ontology/visual-analytics#Multiplicity' ):
                        vcMandatoryList.append(visualChannel)
                        
                entryIndex = entryIndex + 1
                
            if ( len(vcMandatoryList ) != len(self.unique(vcMandatoryList) ) ):
                return 0
            
            # 3b)
            cubeMandatoryList = []
            entryIndex = 0
            for combinationEntry in combinationList:
                if ((  entryIndex % 2 ) == 1 ):
                    cubeComponent = combinationEntry    
                    cubeMandatoryList.append(cubeComponent)
                        
                entryIndex = entryIndex + 1
                
            if ( len(cubeMandatoryList ) != len(self.unique(cubeMandatoryList) ) ):
                return 0
            
            return 1
        except Exception as ex:
            raise Exception("-Mapping.isStructureCompatible: %s"%ex)
        
    #Pack combinations which are computed by combinatorial permutation into a single array of combination bundles
    def packCombinations (self, combinationList, combinationSize ):
        try:
            packedCombinationList = []
        
            packedChartCombinationList = []
            entry = { 'chart': {} , 'cube': {} }
            entryIndex = 0
            packageIndex = 0
            for combinationEntry in combinationList:
                if ((  entryIndex % 2 ) == 0 ):
                    entry = { 'chart': {} , 'cube': {} }
                    entry['chart'] = combinationEntry
                else:
                    entry['cube'] = combinationEntry
                    packedChartCombinationList.append(entry)
                
                entryIndex = entryIndex + 1
                
                if ( len(entry["chart"]) > 0 and len(entry["cube"]) > 0 ):
                    packedCombinationList.append(packedChartCombinationList)
                    packedChartCombinationList = []
               
                packageIndex = packageIndex + 1
               
            return packedCombinationList
        except Exception as ex:
            raise Exception("-Mapping.packCombinations: %s"%ex)  
     
     
                            
                            
        
    '''Combinatorial function - using permutation compute all possible mappings between charts and cube'''    
    def suggestChartsPhase3(self, dimensionList, measureList, chartList):
        try:
            filteredCharts = chartList
            
            cubeComponents = []
            
            validCombinations = []
            
            for measure in measureList:
                cubeComponents.append(measure)
                
            for dimension in dimensionList:
                cubeComponents.append(dimension)    

            #print filteredCharts
            for chart in filteredCharts:
                vcList = chart['visualChannels']
                
                combinedList = [vcList, cubeComponents]
                
                if len( self.unique(vcList) ) == 1:
                    
                    chartCombinationList = []
                    
                    combinationList = ()
                    preliminaryList = []
                    for cubeComponent, visualChannel in zip(cubeComponents, vcList):
                        
                        preliminaryList.append(visualChannel)
                        preliminaryList.append(cubeComponent)
                        
                    combinationList = tuple(preliminaryList)
                    
                    #print "DINGS2 :", combinationList
                    if ( self.isTypeCompatible( combinationList ) ):
                        if ( self.isStructureCompatible(cubeComponents, vcList, combinationList) ):
                            #print "Combination found, chart:", chart['chartName'],"\n"
                            
                            packedCombinations = self.packCombinations(combinationList, len(vcList))
                            chartCombinationList.append(packedCombinations)
                    
                            chartCombinationList = self.unique(chartCombinationList)
                            chartBundle = { 'chartName' : chart['chartName'], 'chartURI' : chart['chartURI'], 'combinations' : chartCombinationList }
                    
                            validCombinations.append(chartBundle)
                else:
                    #now we let the random generator create combinations for about 2 seconds per chart, or if we already have results it should break
                    start_time = datetime.now()
                    
                                    
                    numMaxSuggestions = 20 # we limit the number of suggestions
                    suggestionCnt = 0
                    chartCombinationList = []
                    while( self.millis(start_time) < 50000 ): 
                        combinationList = self.random_product( *combinedList, repeat=len(vcList) )
    
                        if ( self.isTypeCompatible( combinationList ) ):
                            if ( self.isStructureCompatible(cubeComponents, vcList, combinationList) ):
                                #print "Combination found, chart:", chart['chartName'],"\n"
                                suggestionCnt = suggestionCnt + 1
                                
                                packedCombinations = self.packCombinations(combinationList, len(vcList))
                                chartCombinationList.append(packedCombinations)
                                if ( suggestionCnt >= numMaxSuggestions ):
                                    break;
     
                    chartCombinationList = self.unique(chartCombinationList)
                    chartBundle = { 'chartName' : chart['chartName'], 'chartURI' : chart['chartURI'], 'combinations' : chartCombinationList }
                    
                    validCombinations.append(chartBundle)
                
            
            #print validCombinations
            return validCombinations
        except Exception as ex:
            raise Exception("-Mapping.suggestChartsPhase3: %s"%ex)
                
    
    '''Adjust the structure of charts so that we have the same one like in the cube - instantiation of optional visual channels'''    
    def suggestChartsPhase2(self, dimensionList, measureList, chartList):
        try:
            filteredCharts = chartList
            
            # number of visual channels we need
            numRequiredVisualChannels = len(dimensionList) + len(measureList)
            
            for chart in filteredCharts:
                vcList = chart['visualChannels']
                
                #now, we have to look how many visual channels we need to instantiate 
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
            raise Exception("-Mapping.suggestChartsPhase2: %s"%ex)
    
    '''Filter charts based on conformance to the structure (i.e. number of instantiated visual channels)'''
    def suggestChartsPhase1(self, dimensionList, measureList, chartList):
        try:
            filteredCharts = []
            
            # number of visual channels we need
            numRequiredVisualChannels = len(dimensionList) + len(measureList)
            
            for chart in chartList:
                # it is required that # of mandatory + optional visual channels is greater-equal than numRequiredVisualChannels - we can then draw our cube 
                numExistingMandatoryVisualChannels = 0
                numExistingOptionalVisualChannels = 0
                vcList = chart['visualChannels']
                
                for vc in vcList:
                    vcOccurrence = vc['vcOccurrence']
                    vcPersistence = vc['vcPersistence']
                    
                    # if we have occurrence multiplicity - then we can have as many visual channels as we want
                    if ( vcOccurrence == 'http://code-research.eu/ontology/visual-analytics#Multiplicity' ):
                        numExistingMandatoryVisualChannels = numRequiredVisualChannels
                        numExistingOptionalVisualChannels = 0
                        break
                    
                    if ( vcPersistence == 'http://code-research.eu/ontology/visual-analytics#Mandatory' ):
                        numExistingMandatoryVisualChannels = numExistingMandatoryVisualChannels + 1
                    else:
                        numExistingOptionalVisualChannels = numExistingOptionalVisualChannels + 1
                  
                if ( ( numExistingMandatoryVisualChannels + numExistingOptionalVisualChannels ) >= numRequiredVisualChannels ):
                    if ( ( numExistingMandatoryVisualChannels ) <= numRequiredVisualChannels ): # but not too much mandatory channels - because we have nothing to put on there
                        filteredCharts.append(chart)
                
            return filteredCharts
        except Exception as ex:
            raise Exception("-Mapping.suggestChartsPhase1: %s"%ex)
          
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
                  
                chartCombinationList = []
                
                combinationList = ()
                preliminaryList = []
                for cubeComponent, visualChannel in zip(cubeComponents, vcList):
                    
                    preliminaryList.append(visualChannel)
                    preliminaryList.append(cubeComponent)
                    
                combinationList = tuple(preliminaryList)
                
                if ( self.isTypeCompatible( combinationList ) ):
                        if ( self.isStructureCompatible(cubeComponents, vcList, combinationList) ):
                            packedCombinations = self.packCombinations(combinationList, len(vcList))
                            chartCombinationList.append(packedCombinations)
                    
                            chartCombinationList = self.unique(chartCombinationList)
                            chartBundle = { 'chartName' : chart['chartName'], 'chartURI' : chart['chartURI'], 'combinations' : chartCombinationList }
                    
                            validCombinations.append(chartBundle) 
                                       
        return validCombinations           
                     
  