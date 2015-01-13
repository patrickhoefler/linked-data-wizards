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
import json
import csv
from ldva.libs.sparql.utils import SPARQLQuery

class GroupedBarChartGenerator(generator.Generator):
    mappingInfoDimension=None
    mappingInfoMeasure=None
    dimensions=None

    labelOfDimensionArray=[]
    labelOfMeasureArray=[]
    measureContentArray=[]
    codeObject={'code': """
    var loc=config.location;

var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var x0 = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

var x1 = d3.scale.ordinal();

var y = d3.scale.linear()
    .range([height, 0]);

var color = d3.scale.ordinal()
    .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);

var xAxis = d3.svg.axis()
    .scale(x0)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .tickFormat(d3.format(".2s"));

var svg = d3.select("#"+loc).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

/*d3.csv("data.csv", function(error, data) {*/

    var data = @@@DATA@@@;

  var ageNames = d3.keys(data[0]).filter(function(key) { return key !== "State"; });

  data.forEach(function(d) {
    d.ages = ageNames.map(function(name) { return {name: name, value: +d[name]}; });
  });

  x0.domain(data.map(function(d) { return d.State; }));
  x1.domain(ageNames).rangeRoundBands([0, x0.rangeBand()]);
  y.domain([0, d3.max(data, function(d) { return d3.max(d.ages, function(d) { return d.value; }); })]);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Population");

  var state = svg.selectAll(".state")
      .data(data)
    .enter().append("g")
      .attr("class", "g")
      .attr("transform", function(d) { return "translate(" + x0(d.State) + ",0)"; });

  state.selectAll("rect")
      .data(function(d) { return d.ages; })
    .enter().append("rect")
      .attr("width", x1.rangeBand())
      .attr("x", function(d) { return x1(d.name); })
      .attr("y", function(d) { return y(d.value); })
      .attr("height", function(d) { return height - y(d.value); })
      .style("fill", function(d) { return color(d.name); });

  var legend = svg.selectAll(".legend")
      .data(ageNames.slice().reverse())
    .enter().append("g")
      .attr("class", "legend")
      .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

  legend.append("rect")
      .attr("x", width +15)
      .attr("width", 18)
      .attr("height", 18)
      .style("fill", color);

  legend.append("text")
      .attr("x", width + 20)
      .attr("y", 9)
      .attr("dy", ".35em")
      .style("text-anchor", "end")
      .text(function(d) { return d; });
"""}
    results={'code':'', 'errors':[]}

    def __init__(self, mappingInfoForDimension, mappingIngfoForMeasure,  mappingInfoForValue):
        self.mappingInfoDimension=mappingInfoForDimension
        self.mappingInfoMeasure=mappingIngfoForMeasure
        self.mappingInfoValue=mappingInfoForValue
        self.results={'code':'', 'errors': []}

    def transform(self):
        try:
            code=""
            parallelcoordinatesGeneratorRows={}
            xEntries = []
            for element in self.mappingInfoValue:
                xAxisLabel = element['observation']['dimensionlabel0']
                labelForYAxis = element['observation']['dimensionlabel1'] #TODO: hard coded stuff shall be fixed
                #print "xAxisLabel------------------------------------------->", xAxisLabel, "labelForYAxis------------------------------------------->", labelForYAxis


                elementForYAxisArray=[]
                elementForXAxis=xAxisLabel
                elementForYAxis = element['observation']['measurevalue']

                if not elementForYAxis:
                        elementForYAxis = str(0.0)



                valueObj = { labelForYAxis : elementForYAxis }
                if elementForXAxis in parallelcoordinatesGeneratorRows:
                    parallelcoordinatesGeneratorRows[elementForXAxis].append(valueObj)
                else:
                    parallelcoordinatesGeneratorRows[elementForXAxis] =  elementForYAxisArray
                    parallelcoordinatesGeneratorRows[elementForXAxis].append(valueObj)

                xEntries.append(labelForYAxis)

            xEntries = self.unique(xEntries)


            #print "-------------------------------------------> ", parallelcoordinatesGeneratorRows
            strResult = "[ "
            for element in parallelcoordinatesGeneratorRows:
                #print "-------------------------------------------> ", element
                values = parallelcoordinatesGeneratorRows[ element ]

                strValueObject = ""

                strContent = ""
                valueKeys = []
                for value in values:
                    for key in value.keys():
                        valueKeys.append(key)
                        strContent = strContent + '"'+key+'"'+":" + value[key]+","

                strContent = strContent +  '"State": '+ '"'+element+'"'
                #gib nullen dazu
                for xValue in xEntries:
                    if xValue in valueKeys:
                        strContent = strContent
                    else:
                        strContent = strContent + '"'+xValue+'"'+":0.0,"



                '''tempList = list(strContent)
                tempList[len(tempList)-1]=""
                strEndContent = "".join(tempList)'''

                strValueObject = "{" +strContent+ "}, "
                toDictObject = strValueObject
                strResult = strResult + toDictObject


            tempList = list(strResult)
            tempList[len(tempList)-2]=""
            strEndResult = "".join(tempList)
            strResult = strEndResult + "]"






            print"grouped bar chart", (strResult)
            code=self.codeObject['code']
            code=code.replace("@@@DATA@@@", "".join(strResult))
            print "CODE\n", code
            #self.results['code']=code

            self.results['code']=code

            #addRows=self.transformRows(parallelcoordinatesGeneratorRowsArray)


        except Exception as ex:
            raise Exception("-GroupedBarChartGenerator.transform: %s"%ex)

    def unique(self, items):
        found = []
        keep = []

        for item in items:
            if item not in found:
                found.append(item)
                keep.append(item)

        return keep





