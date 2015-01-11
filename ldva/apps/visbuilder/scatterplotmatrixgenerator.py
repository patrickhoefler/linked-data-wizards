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

#import generator
#import rdflib
import copy
#from django.conf import settings


class ScatterPlotMatrixGenerator(object):
    mappingInfoDimension = None
    mappingInfoMeasure = None
    dimensions = None
    labelOfDimensionArray = []
    labelOfMeasureArray = []
    results = {'code':'', 'errors':[]}


    def __init__(self, mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue):
        self.mappingInfoDimension = mappingInfoForDimension
        self.mappingInfoMeasure = mappingIngfoForMeasure
        self.mappingInfoValue = mappingInfoForValue

    def transform(self):
                    
        try:
            self.results = {'code':'', 'errors': [], 'id':''}
            
            #get datatypes
            types = self.getLabelsAndTypes()
            self.results["test"] = ""
            
            columns = self.transformColumns()

            #generate a legend
            #stringList = []
            valueStringDictionary = {}
            legendDictionary = {}
            for rowElement in types:
                if rowElement[1] == "string":
                    valueStringDictionary[rowElement[0]] = []
                    #stringList.append(rowElement[0])
                 
            ###   
            #rows = []
     
            # collect sortable rows (all sortable rows are string types)
            for element in self.mappingInfoValue:
                rowValues = []
                #string types
                for i in range(len(self.mappingInfoDimension)):
                    rowValues.append(element['observation']['dimensionlabel' + str(i)])
                #another types
#!!!#                rowValues.append(element['observation']['measurevalue'])
                
                for i in range(len(self.mappingInfoMeasure)):
                    rowValues.append(element['observation']['measurevalue' + str(i)])
                    
                for index,rowElement in enumerate(types):
                    if rowElement[1] == "string":
                        valueStringDictionary[rowElement[0]].append(rowValues[index])
                 
                ##        
                #rows.append(rowValues)        


            legendDictionary = copy.deepcopy(valueStringDictionary)
            
            # sorted and uniqued the data for legends
            for dictkey in valueStringDictionary:
                sortAndUniqueData = self.uniqueForSortData(sorted(valueStringDictionary[dictkey]))
                legendDictionary[dictkey] = sortAndUniqueData
                valueStringDictionary[dictkey] = self.arrayValueToDictKeyForUniqueData(sortAndUniqueData)
                
                
            
            
            #convert the data to the json format for the scatterplotmatrix
            rows = []

            for element in self.mappingInfoValue:
                
                rowValues = []
     
                for i in range(len(self.mappingInfoDimension)):
                    rowValues.append(element['observation']['dimensionlabel' + str(i)])
                    #!# ms = element['observation']['measurevalue' + '0']
                    #!# #['measurevalue']
                    #!# if not ms:
                    #!#    ms = str(0.0)
                #!# rowValues.append(ms)
                for i in range(len(self.mappingInfoMeasure)):
                    ms = element['observation']['measurevalue' + str(i)]
                    if not ms:
                        ms = str(0.0)
                        
                         
                    bol = self.isReal(ms)    
                    
                    if not bol:
                        ms = str(0.0)      
                        
                    rowValues.append(ms)
                        
                #change string data instead number data values
                dictobjs = {}
                for index,rowElement in enumerate(types):
                    if rowElement[1] == "string":
                        rowValues[index] = valueStringDictionary[rowElement[0]][rowValues[index]]
                    elif rowElement[1] == "decimal":
                        rowValues[index] = float(rowValues[index])
                    elif rowElement[1] == "int":
                        rowValues[index] = int(rowValues[index])        
                                         
                    dictobjs[rowElement[0]] = rowValues[index]

                #assign to json            
                rows.append(dictobjs)
         

            
            rows.append(legendDictionary)
             
            self.results["columns"] = columns
            self.results["rows"] = rows

        

        except Exception as ex:
            raise Exception("-Scatterplotmatrix.transform: %s"%ex)

    
    
    def arrayValueToDictKeyForUniqueData(self,array):
        try:
            dictionaryByName={}
            # iterate array
            for index,element in enumerate(array):
                #if(dictionaryByName[element] != element)
                dictionaryByName[element] = index
    
            return dictionaryByName
        except Exception as ex:
            raise Exception("-Scatterplotmatrix.arrayValueToDictKeyForUniqueData: %s"%ex)
    


    #get return datatype in string and another types
    def getLabelsAndTypes(self):
        try:
            labelTypes = []
            # string types
            for element in self.mappingInfoDimension:
                dimension = element['label']
                labelTypes.append([dimension,"string"])

            #another types
            for element in self.mappingInfoMeasure:
                meas = element['label']
                #meas = element['measureuri']
                #addColumnForYAxis=(meas)
                #splitteColumnentityForYAxis = addColumnForYAxis[addColumnForYAxis.rfind("/")+1:]
                
                splitType = element['datatype'].split('#')
                typename = splitType[len(splitType)-1]
                #labelTypes.append([splitteColumnentityForYAxis,typename])
                
                labelTypes.append([meas,typename])

            ###important
            #hard code change datatypes
            if ["Year","string"] in labelTypes:
                labelTypes[labelTypes.index(["Year","string"] )] = ["Year","int"]
            
            
            
            return(labelTypes)
        
        except Exception as ex:
            raise Exception("-Scatterplotmatrix.getLabelsAndTypes: %s"%ex)


    def uniqueForSortData(self,sortedArray):
        try:
            returnArray = []
            returnArray.append(sortedArray[0])
            
            for element in sortedArray:
                if element != returnArray[len(returnArray)-1]:
                    returnArray.append(element)
                    
            return returnArray
        
        except Exception as ex:
            raise Exception("-Scatterplotmatrix.uniqueForSortData: %s"%ex)


    def transformColumns(self):

        try:
            columns = []
            for element in self.mappingInfoDimension:
                dimension = element['label']
                columns.append(dimension)

            for element in self.mappingInfoMeasure:
                meas = element['label']
                columns.append(meas)
                #meas = element['measureuri']
                #addColumnForYAxis=(meas)
                #splitteColumnentityForYAxis = addColumnForYAxis[addColumnForYAxis.rfind("/")+1:]
                #columns.append(splitteColumnentityForYAxis)

            return(columns)

        except Exception as ex:
            raise Exception("-Scatterplotmatrix.transformColumns: %s"%ex)

    
    def isReal(self, txt):
        try:
            float(txt)
            return True
        except ValueError:
            return False


                