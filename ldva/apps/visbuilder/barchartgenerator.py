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

import generator
import rdflib
from ldva.libs.sparql.utils import SPARQLQuery

class BarChartGenerator(generator.Generator):
    mappingInfoDimension=None
    mappingInfoMeasure=None
    dimensions=None
    
    labelOfDimensionArray=[]
    labelOfMeasureArray=[]
    measureContentArray=[]
    codeObject={'code': """var loc=config.location;var chartWidth=config.width;var chartHeight=config.height;;google.load("visualization", "1", {packages:["corechart"], callback : function drawChart() {var data = new google.visualization.DataTable();@@@COLUMNS@@@@@@ROWS@@@ 
    var options = {hAxis: {title: '@@@HAXIS@@@', titleTextStyle: {color: 'red'}}, vAxis: {title: '@@@VAXIS@@@',  titleTextStyle: {color: 'red'}}, width: chartWidth, height: chartHeight,chartArea:{left:70,top:10,width:"70%",height:"80%"} };var chart = new google.visualization.BarChart(document.getElementById(loc));chart.draw(data, options);}});"""}
    results={'code':'', 'errors':[]}
      
    def __init__(self, mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue, dataset, chartrowIndex):
        self.mappingInfoDimension=mappingInfoForDimension
        self.mappingInfoMeasure=mappingIngfoForMeasure
        
        self.mappingInfoValue=mappingInfoForValue
        self.results={'code':'', 'errors': []}
        
       
    def transform(self):
        try:            
            code=""
            barGeneratorRowsArray=[]
            addColumns=self.transformColumns()
            tableForDim = {'dimension' : ''}
            for entry in self.mappingInfoDimension:
                dim = entry['dimensionuri']
                tableForDim['dimension'] = dim
            
            indexForXAxis = self.getDimensionIndex( "x-Axis")
            for i in range(len(tableForDim)):
                for element in self.mappingInfoValue:
                    xAxis = element['observation']['dimensionlabel%s'% (indexForXAxis)]                            
                    yAxis = element['observation']['measurevalue%s'%(i)]
                    
                    barGeneratorRows=[xAxis, yAxis]
                    barGeneratorRowsArray.append(barGeneratorRows) 
                    barGeneratorRowsArray=self.unique(barGeneratorRowsArray)
                    
            addRows=self.transformRows(barGeneratorRowsArray) 
            
            labelOfDimensions = self.mappingInfoDimension[0]['label']
            labelOfMeasure = self.mappingInfoMeasure[0]['label']
            
             
                     
            code=self.codeObject['code']
            code=code.replace("@@@VAXIS@@@", labelOfDimensions)
            code=code.replace("@@@HAXIS@@@", labelOfMeasure)
            
            code=code.replace("@@@COLUMNS@@@", addColumns)
            code=code.replace("@@@ROWS@@@", addRows)
             
            self.results['code']=code
  
        except Exception as ex:
            raise Exception("-BarGenerator.transform: %s"%ex)         
         
    def unique(self, items):
        found = []
        keep = []
    
        for item in items:
            if item not in found:
                found.append(item)
                keep.append(item)
    
        return keep
                                                   
    def transformColumns(self):
        addColumnForYAxis=None
        addColumnForXAxis=[]
        try:
            for element in self.mappingInfoDimension:   
                dimensionUri=element['dimensionuri'] 
                addColumnForXAxis=dimensionUri   
                    
            for element in self.mappingInfoMeasure:   
                meas=element['measureuri']
                addColumnForYAxis=(meas)  
                splitteColumnentityForYAxis = addColumnForYAxis[addColumnForYAxis.rfind("/")+1:]  
           
                       
            firstColumn="data.addColumn('string','"+addColumnForXAxis+"');"
            secondColumn="data.addColumn('number', '"+str(splitteColumnentityForYAxis)+"');"          
            columns=firstColumn+ secondColumn

            return(columns)
        except Exception as ex:
            raise Exception("-BarGenerator.transformColumns: %s"%ex)
        
        
    def transformRows(self, rowsArray):
        try:
            row=""
            rows=""
                    
            for element in rowsArray:
                x=element[0]
                y1=element[1]         
                
                row="['"+x+"',"+y1+"],"
                rows=rows+row
        
            addRows="data.addRows("+rows+");"           
            tempList = list(rows)
            tempList[len(tempList)-1]=""
            
            strRows="".join(tempList)
            addRows="data.addRows(["+strRows+"]);"  
                     
            return(addRows)
        except Exception as ex:
            raise Exception("-BarGenerator.transformRows: %s"%ex)
    
    def getDimensionIndex(self, channelName):
        try:
            xAxisDimension = ""
        
            mappedDimensionUri = ""
            mappedDimensionLabel = ""
            for clientObj in self.mappingInfoDimension:
                
                cubeComponent = clientObj['cubecomponent']
                if cubeComponent == channelName:
                    mappedDimensionUri = clientObj['dimensionuri']
                    mappedDimensionLabel = clientObj['label']
                    
                    mappedDimensionIndex = clientObj['index']            
                    return mappedDimensionIndex
                
        except Exception as ex:
            raise Exception("-BarGenerator.transformRows: %s"%ex)     