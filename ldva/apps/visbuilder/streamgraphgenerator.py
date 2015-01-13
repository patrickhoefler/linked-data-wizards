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
import math

from ldva.libs.sparql.utils import SPARQLQuery
from django.utils import simplejson

class StreamgraphGenerator(generator.Generator):
    #print "OKAYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYyyyy"
    mappingInfoDimension = None
    mappingInfoMeasure = None
    dimensions = None

    labelOfDimensionArray = []
    labelOfMeasureArray = []
    measureContentArray = []
    codeObject = {'code': """

var loc=config.location;
var brushing = @@@DATA2@@@;
var data1 = @@@DATA@@@;
var chartRoxIndex = @@@CHARTROWINDEX@@@;

var globalIndex = 0;
var globalLegend = [];
var globalClusterData = [];
var brush ;
var svg;


processData(data1["cluster"]);



function drawStreamGraph(numSeries, numSamples){
var n = numSeries, // number of layers
    m = numSamples, // number of samples per layer

    stack = d3.layout.stack().offset("silhouette"),
    layers0 = stack(d3.range(n).map(function() { return generateClusterData(); })  );
    //console.log(layers0);

var width = 1000,
    height = 600;



var dots = "";
var yearArray=[];
var firstObject = data1['cluster'][globalIndex];

var timeslots = firstObject['timeslots'];
for(i = 0;i<timeslots.length;i++){
    var year = timeslots[i]['timeslot'];
    yearArray.push(year);
}
var minYear=yearArray[0];
var maxYear=yearArray[yearArray.length-1];

var x = d3.scale.linear()
    .domain([minYear, maxYear])
    .range([50, width-100]);

var y = d3.scale.linear()
    .domain([0, d3.max(layers0, function(layer) { return d3.max(layer, function(d) { return d.y0 + d.y; }); })])
    .range([height, 0]);

var color = d3.scale.category20();
// defining the domain of the color, so that the sorting gets not lost.
color.domain(_.map(data1.cluster, function(dataObject){ return dataObject.country; }));

var area = d3.svg.area()
    .x(function(d) { return x(d.x); })
    .y0(function(d) { return y(d.y0); })
    .y1(function(d) { return y(d.y0 + d.y); });

svg = d3.select("body").select("#"+loc).append("svg")
    //.attr("width", width)
    //.attr("height", height + 50);
    .attr('class', 'stream')
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("viewBox", "0 0 " + width + " " + (height + 50));

globalIndex = data1["cluster"].length-1;




svg.selectAll("path")
    .data(layers0)

  .enter().append("path")
    .attr("d", area)
     .style("stroke-width", "2")
    .style("fill", function(d) {
        var col = color(data1['cluster'][globalIndex].country);

        var colorText = col;
            var sol = data1['cluster'][globalIndex].country;
            globalLegend.push( {"cluster":data1['cluster'][globalIndex].country, "color": colorText} );
            //console.log(data1['cluster'][globalIndex].country);
            d3.select(this).attr("id", function() { return "IDPREFIX_" + sol.split(" ").join("_"); })
            d3.select(this).style("fill", function() { return col; })
          /*.on("mouseover", function (d) {
                //console.log(d3.select(this))
                  d3.select(this).style("stroke", "black")
                  .style("fill", "black")

                .append("title")
               .text(function(d, i) {

                    return sol;

                })
                 })
                .on("mouseout", function (d) {
                    d3.select(this).style("stroke", "transparent")
                    .style("fill", function(d) { return col; })


                });*/

                globalIndex--;

                return col;
        })

    brush = d3.svg.brush()
        .x(d3.scale.linear().domain([minYear, maxYear])
        .range([50, width-100]))
        .on("brushend", brush);


    var slctArray = []
    brushingObserver.registerListener(function(newChartRowIndex){ chartRowIndex = newChartRowIndex; }, chartRoxIndex, function(selectedData){
           //d3.selectAll("rect").call(brush.clear());


        //console.log(selectedData);

        brush.clear();
        svg.selectAll('.brush').call(brush);

           if ( selectedData == null )   // When the brush is deactivated in another charts.
           {
               selectedData = [];
               for ( cnt = 0; cnt < globalLegend.length; cnt++ )
               {
                    var entry = globalLegend[cnt];
                    var completeName =  entry.cluster;
                    var entryArray = [];

                    entryArray.push(completeName);
                    entryArray.push(completeName);
                    entryArray.push(completeName);

                    selectedData.push(entryArray);
               }
           }
           /*console.log("MOIIIII");
           console.log(selectedData);*/
           drawSelectedData(selectedData);

    });

     svg.append("g")
        .attr("class", "brush")
        .call(brush)
      .selectAll(".stream rect")

        .attr("y", -6)
        .attr("height", height + 7);

    //---------------------------------------------------------------------------
    function drawSelectedData(selectedDataFromOtherChart)
    {
        var selectedNamesArray = getSelectedNames(selectedDataFromOtherChart);
        paintPath(selectedNamesArray);
    }


    //---------------------------------------------------------------------------
    function paintPath( exludeList )
    {
        var pathMainList = svg.selectAll(".stream path");
        var pathList = pathMainList[0];


        for ( var cnt = 0; cnt < pathList.length; cnt++)
        {
            var path = pathList[cnt];
            var pathId = d3.select(path).attr("id");


        /*console.log("brushedata");
           console.log(exludeList);
           console.log("pathID");
           console.log(pathId);*/

            if ( exludeList.indexOf( pathId ) >= 0 )
            {
                //alert("habe ich " + pathId);
                var originalColor = getOriginalColor(pathId);
                d3.select(path).style("stroke", "none")
                      .transition().style("fill", originalColor)
                      .style("opacity", 1.0)
            }
            else
            {

                d3.select(path).style("stroke", "grey")
                      .transition().style("fill", "grey")
                      .style("opacity", 0.4)
            }

        }


    }

    //---------------------------------------------------------------------------
    function getSelectedNames(selectedDataFromOtherChart)
    {
        var selectedNamesArray = [];
        for ( cnt = 0; cnt < selectedDataFromOtherChart.length; cnt++)
        {
            var point = selectedDataFromOtherChart[cnt];
            selectedNamesArray.push("IDPREFIX_" + point[1].split(" ").join("_"));
        }

        return selectedNamesArray;
    }

    //---------------------------------------------------------------------------
    function getOriginalColor( countryName )
    {


        for ( var cnt = 0; cnt < globalLegend.length; cnt ++ )
        {
            var entry = globalLegend[cnt];

            var completeName = "IDPREFIX_" + entry.cluster;

            if ( completeName.split(" ").join("_") == countryName.split(" ").join("_") )
            {
                return entry.color;
            }
        }

        return "#cccccc";
    }


    //---------------------------------------------------------------------------

function brush() {
    selectedData = [];
               for ( cnt = 0; cnt < globalLegend.length; cnt++ )
               {
                    var entry = globalLegend[cnt];
                    var completeName =  entry.cluster;
                    var entryArray = [];

                    entryArray.push(completeName);
                    entryArray.push(completeName);
                    entryArray.push(completeName);

                    selectedData.push(entryArray);
               }

           /*console.log("MOIIIII");
           console.log(selectedData);*/
           drawSelectedData(selectedData);





    var time=[];
    var e = brush.extent();

    var va1=e[0];
    var va2=e[1];


    var selectData=[];
    for(i=0;i<e.length;i++){
     time.push(Math.floor(e[i]));
    }
    /*console.log("E begin");
    console.log(time);
    console.log("E end");*/

    selectData=getSelectedData(time);
    if( va1 == va2 ){


      for ( cnt = 0; cnt < globalLegend.length; cnt++ )
               {
                    var entry = globalLegend[cnt];
                    var completeName =  entry.cluster;
                    var entryArray = [];

                    entryArray.push(completeName);
                    entryArray.push(completeName);
                    entryArray.push(completeName);

                    selectData.push(entryArray);
               }

           drawSelectedData(selectData);
           selectData = [];

    }

    //console.log(selectData);
    brushingObserver.update(chartRoxIndex, selectData);


}



    var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom").tickFormat(d3.format("04d")).ticks(yearArray.length);

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0," + (height) + ")")
        .call(xAxis)
        .append("text")
        .attr("class", "label")
        .attr("x", width-80)
         .attr("y", -9)
        .style("text-anchor", "end")
            .text("Year")
        .on('click', function(){
            Vis.view.getNewAxisLabel("Year", function(newAxisLabel){ svg.select("g.axis text.label").text(newAxisLabel); });
        });


var legendStrings = [];
var legendColor = [] ;
for (var i = (globalLegend.length)-1; i>=0; i--)    {
        var clusterName = globalLegend[i].cluster;
        var colorName = globalLegend[i].color;
        legendStrings.push(clusterName);
        legendColor.push(colorName);
}
var color = d3.scale.ordinal()
    .range(legendColor);

var legend = svg.selectAll(".legend")
      .data(legendStrings)
    .enter().append("g")
      .attr("class", "legend")
      .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

     //console.log(legendColor);
      legend.append("rect")
      .attr("x", width - 20)
      .attr("width", 18)
      .attr("height", 18)
      .style("fill",color).on("mouseover", function (d) {

                var zName = "IDPREFIX_" + d.split(" ").join("_");

                d3.selectAll("path#"+zName).style("stroke", "black").style("stroke-width", "7");

            })
            .on("mouseout", function (d) {
                var zName = "IDPREFIX_" + d.split(" ").join("_");
                d3.selectAll("path#"+zName).style("stroke", "transparent")
            });


      legend.append("text")
      .attr("x", width - 30)
      .attr("y", 9)
      .attr("dy", ".35em")
      .style("text-anchor", "end")
      .text(function(d) {return d; });


  //-----------------------------------------------------------------------------------------------------------------------

    function getSelectedData(e){

    var va1=e[0];
    var va2=e[1];

    var cluster = data1.cluster;
    var streamArray = []  ;
    var strgStream = [];
   for (var i = 0; i<cluster.length;i++){
        var country = cluster[i]['country'];
        timeslots =  cluster[i]['timeslots'];
        for (var j= 0; j<timeslots.length; j++){
            var timeslot = timeslots[j]['timeslot'];
            var value = timeslots[j]['value'];
            if( timeslot>=va1 && timeslot<= va2 ){
                strgStream.push([ timeslot, country, parseFloat( value)]);

             }
          }

   }
/*console.log(va1);
console.log(va2);
console.log(strgStream); */
  return strgStream;
}


function getStreamPoint(year1, yCoord)
    {

    //console.log(layers0);
        for ( var xx = 0; xx < layers0.length ; xx++)
        {
            var xLayer = layers0[xx];

            for ( var yy=0; yy<xLayer.length; yy++)
            {
                var xLayerPart = xLayer[yy];
                //console.log(xLayerPart);

                if ( xLayerPart.x == year1 && xLayerPart.y0 <= yCoord)
                {
                    /*console.log("found");
                    console.log(xLayerPart);*/
                    return xLayerPart;
                }
            }
        }
    }






}

//-------------------------------- End of the draw function ------------------------------------------------------------

function generateClusterData(){
    --globalIndex;



    var yearArray=[];
    var firstObjectForYearCounter = data1['cluster'][0];
    var timeslotsForYearCounter = firstObjectForYearCounter['timeslots'];
    for(i = 0;i<timeslotsForYearCounter.length;i++){
        var yearForCounter = timeslotsForYearCounter[i]['timeslot'];
        yearArray.push(yearForCounter);
    }
    var minYear = yearArray[0];
    var maxYear = yearArray[yearArray.length-1];
    var lengthOfYearArray = yearArray.length;

    var firstObject = data1['cluster'][globalIndex];
    var timeslots = firstObject['timeslots'];
    var dataPointArray = [];



    if(timeslots.length == lengthOfYearArray){
        for(i = 0;i<timeslots.length;i++){
            var year = timeslots[i]['timeslot'];
            var value = timeslots[i]['value'];


            var intYear = parseInt(year);
            var floatValue = parseFloat(value);
            var dataPointObject = {x:intYear, y:floatValue, label:"'"+intYear+"'"};
            //console.log("DP: " + dataPointObject.x + ", v: " + dataPointObject.y + ", Y: " + dataPointObject.label)
            dataPointArray.push(dataPointObject);
        }
    }
    else{
        for(i=minYear;i<=maxYear;i++){

            var dataPointObject = {x:i, y:0.0, label:"'"+year+"'"};
            dataPointArray.push(dataPointObject);
        }
    }

    return(dataPointArray);

}

function processData(clusterArray){
    if(clusterArray == "undefined"){
        alert("processData: Cannot read data for drawing.");
        return;
    }

    /*console.log('jjjjjjjjjjjjjjjjjj');
    console.log(clusterArray);*/

    var n=clusterArray.length;
    var firstObject = clusterArray[0];

    var timeSlotsArray=firstObject['timeslots'];
    var m=timeSlotsArray.length;

    globalIndex = n;
    globalClusterData = clusterArray;
    drawStreamGraph( n, m, {});

    //drawLegend(globalLegend, loc);
    //globalLegend = [];
}






function getRawDataFromPath(path)  {
    var returnDataRow = [];
        returnDataRow[0] = 0;
        return;

}


"""}


    results={'code':'', 'errors':''}

    def __init__(self, mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue, dataset, chartrowIndex):
        self.mappingInfoDimension = mappingInfoForDimension
        self.mappingInfoMeasure = mappingIngfoForMeasure

        self.mappingInfoValue = mappingInfoForValue
        self.chartRoxIndex = chartrowIndex
        self.results = {'code':'', 'errors': ''}

    def transform(self):
        try:
            code = ""
            streamgraphGeneratorRows = {}
            streamgraphGeneratorRowsArray = []



            index = ""
            index2 = ""
            labelForYear = self.defineDate()
            #print "1---------------------------------------------------->", labelForYear
            labelForEntry = self.defineString()
            #print "2---------------------------------------------------->", labelForEntry
            for element in labelForYear:
                    index = element['index']
                    #print "indexxxxxxxxxxxxxxxxxxxxxxxx", index

            for el in labelForEntry:
                    index2 = el['index']

            labelForYear = self.unique(labelForYear)
            streamGraphObject = {"year":'' , "timeslots": ''}
            streamGraphObjectForDrawing = {'cluster':[]}
            for element in self.mappingInfoValue:
                xAxisLabel = element['observation']['dimensionlabel%s'%index2]
                country = element['observation']['dimensionlabel%s'%index]

                elementForYAxisArray = []
                yAxisValue = element['observation']['measurevalue%s'%0]


                if not yAxisValue:
                    yAxisValue = "0.0"

                if xAxisLabel in streamgraphGeneratorRows:
                    valueObj = []
                    valueObj = {"timeslot": country, "value":yAxisValue}
                    streamgraphGeneratorRows[xAxisLabel]["timeslots"].append(valueObj)

                else:
                    streamgraphGeneratorRows[xAxisLabel] =  {}
                    streamgraphGeneratorRows[xAxisLabel]["country"] =  xAxisLabel
                    streamgraphGeneratorRows[xAxisLabel]["timeslots"] =  elementForYAxisArray



                    valueObj = []
                    valueObj = {"timeslot": country, "value":yAxisValue}
                    streamgraphGeneratorRows[xAxisLabel]["timeslots"].append(valueObj)


            for elements in streamgraphGeneratorRows:
                year = streamgraphGeneratorRows[elements]
                timeslots = year["timeslots"]
                myEntity = year["country"]

                timeslots.sort()
                streamGraphObject = {"timeslots":timeslots, "country":myEntity}
                streamgraphGeneratorRowsArray.append(streamGraphObject)

            streamgraphGeneratorRowsArray.sort()
            streamGraphObjectForDrawing = {"cluster":streamgraphGeneratorRowsArray}
            code=self.codeObject['code']


            cluster = streamGraphObjectForDrawing['cluster']

            maxLength = 0
            maxElements = {}
            for element in cluster:
                lengthOfTimeSlots =  len(element['timeslots'])
                if lengthOfTimeSlots > maxLength:
                    maxLength = lengthOfTimeSlots
                    maxElements = element['timeslots']



            for maxs in maxElements:
                timeslotOfMax = maxs['timeslot']
                valueMax = maxs['value']
                for element in cluster:
                    timeslotsArray = element['timeslots']

                    isFound = False

                    for el in timeslotsArray:
                        timeslot = el['timeslot']
                        if timeslot == timeslotOfMax:
                            isFound = True


                    if isFound == False:
                        if float(valueMax):
                            newtimeObject = {'value':"0.0", 'timeslot': timeslotOfMax}

                        else:
                            newtimeObject = {'value':"0", 'timeslot': timeslotOfMax}

                        timeslotsArray.append (newtimeObject)
                        timeslotsArray.sort()

            labelForYear = self.unique(labelForYear)



            strgStream = []
            streamArray = []
            for stream in cluster:
                country = stream['country']
                timeslots = stream['timeslots']
                for time in timeslots:
                    timeslot = time['timeslot']
                    value = time['value']
                    strgStream.append ([timeslot, country, float(value)])


            text_file = open("Output.txt", "w")
            text_file.write(simplejson.dumps(streamGraphObjectForDrawing))
            text_file.close()

            if len(labelForYear) >2:
                code = code.replace("@@@DATA@@@", simplejson.dumps(streamGraphObjectForDrawing))
                code = code.replace("@@@DATA2@@@", simplejson.dumps(strgStream ))
                code = code.replace("@@@CHARTROWINDEX@@@", self.chartRoxIndex )
                self.results['code'] = code
            else:
                self.results['errors'] = "True"

        except Exception as ex:
            raise Exception("-StreamgraphGenerator.transform: %s"%ex)




    def defineDate (self):

        minx = 1900
        maxx = 2100
        labelArray = []

        for i in range(len(self.mappingInfoDimension)-1):
            for element in self.mappingInfoValue:
                label = element['observation']['dimensionlabel%s'%i]
                if label.isdigit():

                    if ( int(label) >= minx and int(label) <= maxx):
                        labelObject = {'label':label, 'index':i}

                        labelArray.append(labelObject)

        return labelArray



    def  defineString (self):
        labelArray = []
        for i in range(len(self.mappingInfoDimension)):
            for element in self.mappingInfoValue:
                label = element['observation']['dimensionlabel%s'%i]
                if not label.isdigit():
                    labelObject = {'label':label, 'index':i }
                    labelArray.append(labelObject)


        return labelArray






    def unique(self, items):
        found = []
        keep = []

        for item in items:
            if item not in found:
                found.append(item)
                keep.append(item)

        return keep
