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

class D3PieChartGenerator(generator.Generator):
    mappingInfoDimension=None
    mappingInfoMeasure=None
    dimensions=None

    labelOfDimensionArray=[]
    labelOfMeasureArray=[]
    measureContentArray=[]
    codeObject={'code': """

var loc=config.location;
var w = 900,

h = 600,

r = 300,

color = d3.scale.category20();



var data = @@@DATA@@@;

var vis = d3.select("body")
.select("#"+loc)
.append("svg:svg")

.data([data])

.attr("width", w)

.attr("height", h)

.append("svg:g")

.attr("transform", "translate(" + r + "," + r + ")")



var arc = d3.svg.arc()

.outerRadius(r);



var pie = d3.layout.pie()

.value(function(d) { return d.value; });



var arcs = vis.selectAll("g.slice")

.data(pie)
.enter()

.append("svg:g")

.attr("class", "slice");


arcs.append("svg:path")

.attr("fill", function(d, i) { return color(i); } )

.attr("d", arc);



arcs.append("svg:text")

.attr("transform", function(d) {


d.innerRadius = 0;

d.outerRadius = r;

return "translate(" + arc.centroid(d) + ")";
})

.attr("text-anchor", "middle")
.text(function(d, i) { return data[i].label; });

"""}
    results={'code':'', 'errors':[]}

    def __init__(self, mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue):
        self.mappingInfoDimension=mappingInfoForDimension
        self.mappingInfoMeasure=mappingIngfoForMeasure
        self.mappingInfoValue=mappingInfoForValue
        self.results={'code':'', 'errors': []}

    def transform(self):
        try:
            code=""
            d3PieChartGeneratorRowsArray=[]

            indexForXAxis = self.getDimensionIndex( "x-Axis")


            for element in self.mappingInfoValue:
                xAxisLabel = element['observation']['dimensionlabel%s'% (indexForXAxis)]
                yAxisValue = element['observation']['measurevalue']


                d3PieChartGeneratorRows=[xAxisLabel, yAxisValue]
                d3PieChartGeneratorRowsArray.append(d3PieChartGeneratorRows)
                d3PieChartGeneratorRowsArray=self.unique(d3PieChartGeneratorRowsArray)


            addRows=self.transformRows(d3PieChartGeneratorRowsArray)
            code=self.codeObject['code']

            code=code.replace("@@@DATA@@@", addRows)

            self.results['code']=code


        except Exception as ex:
            raise Exception("-PieChartGenerator.transform: %s"%ex)

    def unique(self, items):
        found = []
        keep = []

        for item in items:
            if item not in found:
                found.append(item)
                keep.append(item)

        return keep



    def transformRows(self, rowsArray):
        try:
            row=""
            rows=""

            for element in rowsArray:
                x=element[0]
                y1=element[1]


                row="{'label':'"+x+"','value':"+y1+"},"
                rows=rows+row

            tempList = list(rows)
            tempList[len(tempList)-1]=""

            strRows="".join(tempList)
            addRows="["+strRows+"];"

            return(addRows)
        except Exception as ex:
            raise Exception("-PieChartGenerator.transformRows: %s"%ex)

    def getDimensionIndex(self, channelName):
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
