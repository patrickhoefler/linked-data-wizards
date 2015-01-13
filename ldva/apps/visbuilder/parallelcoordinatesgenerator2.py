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
from ldva.libs.sparql.utils import SPARQLQuery

class ParallelGenerator(generator.Generator):
    mappingInfoDimension = None
    mappingInfoMeasure = None
    dimensions = None
    codeObject = {'code': """var loc=config.location; function drawParallelCoordinates(){    var m = [30, 10, 10, 10],        w = 960 - m[1] - m[3],        h = 500 - m[0] - m[2];    var x = d3.scale.ordinal().rangePoints([0, w], 1),        y = {};    var line = d3.svg.line(),        axis = d3.svg.axis().orient("left"),        background,        foreground;    var svg = d3.select("#"+loc).append("svg:svg")        .attr("width", w + m[1] + m[3])        .attr("height", h + m[0] + m[2])      .append("svg:g")        .attr("transform", "translate(" + m[3] + "," + m[0] + ")");        var dataForCoordinates = @@@DATA@@@; x.domain(dimensions = d3.keys(dataForCoordinates[0]).filter(function(d) {        return d != "name" && (y[d] = d3.scale.linear()            .domain(d3.extent(dataForCoordinates, function(p) { return +p[d]; }))            .range([h, 0]));      }));            background = svg.append("svg:g")          .attr("class", "background")        .selectAll("path")          .data(dataForCoordinates)        .enter().append("svg:path")          .attr("d", path);            foreground = svg.append("svg:g")          .attr("class", "foreground")        .selectAll("path")          .data(dataForCoordinates)        .enter().append("svg:path")          .attr("d", path);           var g = svg.selectAll(".dimension")          .data(dimensions)        .enter().append("svg:g")          .attr("class", "dimension")          .attr("transform", function(d) { return "translate(" + x(d) + ")"; });            g.append("svg:g")          .attr("class", "axis")          .each(function(d) { d3.select(this).call(axis.scale(y[d])); })        .append("svg:text")          .attr("text-anchor", "middle")          .attr("y", -9)          .text(String);            g.append("svg:g")          .attr("class", "brush")          .each(function(d) { d3.select(this).call(y[d].brush = d3.svg.brush().y(y[d]).on("brush", brush)); })        .selectAll("rect")          .attr("x", -8)          .attr("width", 16);            function path(d) {      return line(dimensions.map(function(p) { return [x(p), y[p](d[p])]; }));    }        function brush() {      var actives = dimensions.filter(function(p) { return !y[p].brush.empty(); }),          extents = actives.map(function(p) { return y[p].brush.extent(); });      foreground.style("display", function(d) {        return actives.every(function(p, i) {          return extents[i][0] <= d[p] && d[p] <= extents[i][1];        }) ? null : "none";      });    }} drawParallelCoordinates();"""}

    def __init__(self, mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue):
        #print ("First Phase Mapping",firstPhaseMapping )
        #print ("First Phase Mapping For Measure",firstPhaseMappingForMeasure )
        self.mappingInfoDimension = mappingInfoForDimension
        self.mappingInfoMeasure = mappingIngfoForMeasure
        self.mappingInfoValue = mappingInfoForValue
        #print "VALUEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE_NEU", self.mappingInfoValue
        self.results = {'code':'', 'errors': []}

    '''def transform(self):

        try:
            code=""
            #parallelcoordinatesGeneratorRows={}
            tableForDim = {'dimension' : ''}
            for entry in self.mappingInfoDimension:
                dim = entry['dim']
                tableForDim['dim'] = dim


            for i in range(len(tableForDim)-1):
                parallelcoordinatesGeneratorRows={}
                for element in self.mappingInfoValue:
                    x-Axis = element['observation']['dimensionlabel%s'% (i+1)]
                    line = element['observation']['dimensionlabel%s'% (i)]

                    yAxisArray=[]
                    elementForXAxis=x-Axis
                    yAxis = element['observation']['measurevalue']
                    #print "O:OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOo", yAxis

                    valueObj = { line : yAxis }
                    if elementForXAxis in parallelcoordinatesGeneratorRows:
                        parallelcoordinatesGeneratorRows[elementForXAxis].append(valueObj)
                    else:
                        parallelcoordinatesGeneratorRows[elementForXAxis] =  yAxisArray
                        parallelcoordinatesGeneratorRows[elementForXAxis].append(valueObj)

            strResult = "[ "
            for element in parallelcoordinatesGeneratorRows:
                values = parallelcoordinatesGeneratorRows[ element ]

                strValueObject = ""

                strContent = ""
                for value in values:
                    for key in value.keys():
                        strContent = strContent + '"'+key+'"'+":" + value[key]+","

                tempList = list(strContent)
                tempList[len(tempList)-1]=""
                strEndContent = "".join(tempList)

                strValueObject = "{" +strEndContent+ "}, "
                toDictObject = strValueObject
                strResult = strResult + toDictObject


            tempList = list(strResult)
            tempList[len(tempList)-2]=""
            strEndResult = "".join(tempList)
            strResult = strEndResult + " ]"

            print"parallel coordinates", (strResult)
            code=self.codeObject['code']
            #code=code.replace("@@@DATA@@@", "".join(strResult))
            code=code.replace("@@@DATA@@@", "".join(strResult))
            print "CODE\n", code
            #self.results['code']=code

            self.results['code']=code

            #addRows=self.transformRows(parallelcoordinatesGeneratorRowsArray)


        except Exception as ex:
                raise Exception("-ParallelcoordinatesGenerator.transform: %s"%ex) '''


    def transform(self):

        try:
            code=""
            #parallelcoordinatesGeneratorRows={}
            tableForDim = {}
            xEntries = []
            tableForDimArray= []
            for entry in self.mappingInfoDimension:
                dim = entry['dimensionuri']
                tableForDim = {'dimension' : ''}
                tableForDim['dimension'] = dim
                tableForDimArray.append(tableForDim)


            for i in range(len(tableForDimArray)-1):
                parallelcoordinatesGeneratorRows = {}
                for element in self.mappingInfoValue:
                    xAxis = element['observation']['dimensionlabel%s'% (i+1)]
                    line = element['observation']['dimensionlabel%s'% (i)]

                    yAxisArray = []
                    elementForXAxis = xAxis
                    yAxis = element['observation']['measurevalue']
                    #print "O:OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOo", line

                    valueObj = { line : yAxis }
                    if elementForXAxis in parallelcoordinatesGeneratorRows:
                        parallelcoordinatesGeneratorRows[elementForXAxis].append(valueObj)
                    else:
                        parallelcoordinatesGeneratorRows[elementForXAxis] =  yAxisArray
                        parallelcoordinatesGeneratorRows[elementForXAxis].append(valueObj)

                    xEntries.append(line)

            xEntries = self.unique(xEntries)



            strResult = "[ "
            for element in parallelcoordinatesGeneratorRows:
                values = parallelcoordinatesGeneratorRows[ element ]
                print "values", values
                strValueObject = ""

                strContent = ""
                valueKeys = []
                for value in values:
                    for key in value.keys():
                        valueKeys.append(key)
                        strContent = strContent + '"'+key+'"'+":" + value[key]+","

                #gib nullen dazu
                for xValue in xEntries:
                    if xValue in valueKeys:
                        strContent = strContent
                    else:
                        strContent = strContent + '"'+xValue+'"'+":0.0,"

                tempList = list(strContent)
                tempList[len(tempList)-1]=""
                strEndContent = "".join(tempList)

                strValueObject = "{" +strEndContent+ "}, "
                toDictObject = strValueObject
                strResult = strResult + toDictObject


            tempList = list(strResult)
            tempList[len(tempList)-2]=""
            strEndResult = "".join(tempList)
            strResult = strEndResult + "]"

            #print"parallel coordinates", (strResult)
            code=self.codeObject['code']
            code=code.replace("@@@DATA@@@", "".join(strResult))
            #print "CODE\n", code
            #self.results['code']=code

            self.results['code']=code

            #addRows=self.transformRows(parallelcoordinatesGeneratorRowsArray)


        except Exception as ex:
            raise Exception("-ParallelGenerator.transform: %s"%ex)


    def unique(self, items):
        found = []
        keep = []

        for item in items:
            if item not in found:
                found.append(item)
                keep.append(item)

        return keep


