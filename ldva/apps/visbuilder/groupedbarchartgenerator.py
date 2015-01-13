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
import csv
from ldva.libs.sparql.utils import SPARQLQuery
from django.utils import simplejson

class GroupedBarChartGenerator(generator.Generator):
    mappingInfoDimension=None
    mappingInfoMeasure=None
    dimensions=None

    labelOfDimensionArray=[]
    labelOfMeasureArray=[]
    measureContentArray=[]
    codeObject={'code': """


var loc=config.location;
var chartRoxIndex = @@@CHARTROWINDEX@@@;
var firstDim = "@@@FIRSTDIM@@@";
var globalLegend = [];

var margin = {top: 20, right: 20, bottom: 165, left: 40},
    width = 960 - margin.left - margin.right,
    height = 700 - margin.top - margin.bottom;

var x0 = d3.scale.ordinal()
    .rangeRoundBands([0, width-100], .1);


var x1 = d3.scale.ordinal();

var y = d3.scale.linear()
    .range([height, 0]);


var color = d3.scale.category20();


var xAxis = d3.svg.axis()
    .scale(x0)
    .orient("bottom");


var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .tickFormat(d3.format(".2s"));





var svg = d3.select("#"+loc).append("svg")
    //.attr("width", width + margin.left + margin.right)
    //.attr("height", height + margin.top + margin.bottom)
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("viewBox", "0 0 " + (width + margin.left + margin.right) + " " + (height + margin.top + margin.bottom))
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

 var brush = d3.svg.brush()
        .x(x0)
       .on("brush", brush)
       .on("brushend", brush);


  svg.append("g")
        .attr("class", "brush")
        .call(brush)
      .selectAll("rect")

        .attr("y", -6)
        .attr("height", height + 7);

/*d3.csv("data.csv", function(error, data) {*/

    var data = @@@DATA@@@;

     var ageNames = d3.keys(data[0]).filter(function(key) { return key !== "State" && key !== "id"; });


  data.forEach(function(d) {

    var sa= d.State;
    var id = d.id;
    d.ages = ageNames.map(function(name) { return {name: name, value: +d[name], state: sa, id: id}; });
   //console.log(d.ages);
  });

  x0.domain(data.map(function(d) { return d.State; }).sort());
  x1.domain(ageNames).rangeRoundBands([0, x0.rangeBand()].sort());
  y.domain([0, d3.max(data, function(d) { return d3.max(d.ages, function(d) { return d.value; }); })].sort());



  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
      .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", function(d) {

                return "rotate(-65)"
                });


     svg.select("g.x.axis")
            .append("text")
            .attr("class", "label")
            .attr("x", width-70)
            .attr("y", -6)
            .style("text-anchor", "end")
            .text("@@@LABEL@@@")
            .on('click', function(){
                Vis.view.getNewAxisLabel("@@@LABEL@@@", function(newAxisLabel){ svg.select("g.x.axis text.label").text(newAxisLabel); });
            });


  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
    .attr("class", "label")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("@@@LABELY@@@")
      .on('click', function(){
                Vis.view.getNewAxisLabel("@@@LABELY@@@", function(newAxisLabel){ svg.select("g.y.axis text.label").text(newAxisLabel); });
            });





  var state = svg.selectAll(".state")
      .data(data)
    .enter().append("g")
      .attr("class", "g")
      .attr("transform", function(d) {return "translate(" + x0(d.State) + ",0)"; });




    //---------------------------------------------------------------------------




  state.selectAll("rect")

      .data(function(d) { return d.ages; })
    .enter().append("rect")
    .attr("class", "rect-background")

      .attr("width", x1.rangeBand())
      .attr("x", function(d) { return x1(d.name); })
      .attr("y", function(d) { return y(d.value); })
      .attr("id", function(d) { /*if (IsNumeric(d.name.split(" ").join("_"))){
          return "IDPREFIX_" + d.name.split(" ").join("_") + d.state.split(" ").join("_");

      }
      else if(IsNumeric(d.state.split(" ").join("_"))){

          return "IDPREFIX_" + d.state.split(" ").join("_") + d.name.split(" ").join("_");

      }
      else if (!IsNumeric(d.name.split(" ").join("_")) && !IsNumeric(d.state.split(" ").join("_"))) {


           return "IDPREFIX_" + d.name.split(" ").join("_") + d.state.split(" ").join("_");
      }*/

      if(d.id == firstDim){
          return "IDPREFIX_" + d.state.split(" ").join("_") + d.name.split(" ").join("_");

      }
      else{

      return "IDPREFIX_" + d.name.split(" ").join("_") + d.state.split(" ").join("_");

      }



      })

      //.attr("idone", function(d) { return "IDPREFIX_" + d.state.split(" ").join("_"); })
      .attr("data", function (d) {

            /*if (IsNumeric(d.name.split(" ").join("_"))){
                globalLegend.push( {"cluster": d.name.split(" ").join("_"), "color":  color(d.name), "state": d.state.split(" ").join("_")} );
             }
             else if (IsNumeric(d.state.split(" ").join("_"))) {

                 globalLegend.push( {"cluster": d.state.split(" ").join("_"), "color":  color(d.name), "state": d.name.split(" ").join("_")} );

             }

            else if (!IsNumeric(d.name.split(" ").join("_")) && !IsNumeric(d.state.split(" ").join("_"))) {


              globalLegend.push( {"cluster": d.name.split(" ").join("_"), "color":  color(d.name), "state": d.state.split(" ").join("_")} );
          } */


            if(d.id == firstDim){
                globalLegend.push( {"cluster": d.state.split(" ").join("_"), "color":  color(d.name), "state": d.name.split(" ").join("_")} );


            }
            else{

            globalLegend.push( {"cluster": d.name.split(" ").join("_"), "color":  color(d.name), "state": d.state.split(" ").join("_")} );

            }





                /*console.log("hiiii");
                console.log(globalLegend);*/


                return  d.name + "," + d.value + ","+ d.state;


             } )
      .attr("height", function(d) { return height - y(d.value); })
      .style("stroke-width", "2")
      .style("fill", function(d) { return color(d.name); })
      .on("mouseover", function (d) {

                  d3.select(this).style("stroke", "black")
                  .style("fill", "black")

                .append("title")
               .text(function(d, i) {

                    return d.name + "," + d.value + ","+ d.state;

            })
             })
            .on("mouseout", function (d) {
                d3.select(this).style("stroke", "transparent")
                .style("fill", function(d) { return color(d.name); })


            });






  function getClassName(label){
        var replacer = new RegExp(" ","g");
        var className = label.replace(replacer, "-").toLowerCase();
        return className;
    }

  var legend = svg.selectAll(".legend")
      .data(ageNames.slice().reverse().sort())
    .enter().append("g")
      .attr("class", "legend")
      .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

  legend.append("rect")
      .attr("x", width -18)
      .attr("width", 18)
      .attr("height", 18)
      .style("fill", color)
      .text(function(d) { return d; })
      .on("mouseover", function (d) {

                var zName = "IDPREFIX_" + d.split(" ").join("_");
                //console.log(d3.selectAll("rect#"));
              //console.log(d3.select(".xAxis" + d+ " .rect-background").style("stroke", "black"));
               d3.selectAll("rect#"+zName).style("stroke", "black");
                //d3.select(".label-" + labelClassName+ " .rect-background").style("display", "none");
            })
            .on("mouseout", function (d) {
                var zName = "IDPREFIX_" + d.split(" ").join("_");
                d3.selectAll("rect#"+zName).style("stroke", "transparent")
            });

  legend.append("text")
      .attr("x", width - 24)
      .attr("y", 9)
      .attr("dy", ".35em")
      .style("text-anchor", "end")
      .text(function(d) {  return d; });






     //---------------------------------------------------------------------------

       function brush() {

       selectedData = [];
               for ( cnt = 0; cnt < globalLegend.length; cnt++ )
               {
                    var entry = globalLegend[cnt];
                    var completeName =  entry.cluster;
                    var completeNameOne = entry.state;

                    var entryArray = [];

                    entryArray.push(completeName);
                    entryArray.push(completeNameOne);
                    entryArray.push(completeName);

                    selectedData.push(entryArray);
               }


    drawSelectedData(selectedData);



         var time=[];
         var e = brush.extent();
         var selectData = getSelectedData(e);


        //drawSelectedData(selectData);

         var va1=e[0];
         var va2=e[1];


         if(va1 == va2 ){
         selectData = [];


         }



         //console.log(d3.selectAll('rect'));
          /*console.log('###########################');
         console.log(selectData);*/
         brushingObserver.update(chartRoxIndex, selectData);
}



  //-----------------------------------------------------------------------------------------------------------------------

    function getSelectedData(e){

    var va1=e[0];
    var va2=e[1];

    var arr = [];
    for(var i = 0; i < d3.selectAll('.rect-background')[0].length; i++){
        var str = d3.select($('.rect-background')[i].parentNode).attr('transform');
        //console.log(d3.select($('.rect-background')[i].parentNode));
        var first = str.substring(10, str.indexOf(",") );

        var x = d3.select($('rect')[i]).attr('x');
        var sum = parseInt(first) + parseInt(x);
        /*console.log(first);
        console.log(x);
        console.log(sum);*/

        if(sum >= va1 && sum <= va2 ){
            var rect = ( d3.select($('.rect-background')[i]).attr('data'));
            /*console.log('daaaaaaa');
            console.log(rect);*/
            var split  = rect.split(',');
            var dimOne = split[0];
            var value = split[1];
            var dimTwo = split[2];


            if (IsNumeric(dimOne)){

                arr.push([dimOne, dimTwo, parseFloat(value)]);


            }
            else{
                arr.push([dimTwo, dimOne, parseFloat(value)]);
            }
        }


    }
/*console.log("hi");
console.log(arr);*/
return arr;

}

function IsNumeric(input)
{
    return (input - 0) == input && (input+'').replace(/^\s+|\s+$/g, "").length > 0;
}
  //----------------------------------------------------------------------------------------------------



brushingObserver.registerListener(function(newChartRowIndex){ chartRowIndex = newChartRowIndex; }, chartRoxIndex, function(selectedData){
/*console.log("hieerr");
    console.log(selectedData);*/

    //d3.select("rect").call(brush.clear());

     brush.clear();
        svg.selectAll('.brush').call(brush);

     /*brush.clear();
       .on("brush", brush)
       .on("brushend", brush)
        .call(brush)
      .selectAll("rect")

        .attr("y", -6)
        .attr("height", height + 7);

        svg.selectAll('.brush').call(brush);*/

     if ( selectedData == null )   // When the brush is deactivated in another charts.
           {
               selectedData = [];
               for ( cnt = 0; cnt < globalLegend.length; cnt++ )
               {
                    var entry = globalLegend[cnt];
                    var completeName =  entry.cluster;
                    var completeNameOne = entry.state;

                    var entryArray = [];

                    entryArray.push(completeName);
                    entryArray.push(completeNameOne);
                    entryArray.push(completeName);

                    selectedData.push(entryArray);
               }
           }





    drawSelectedData(selectedData);

    });


 //---------------------------------------------------------------------------
    function drawSelectedData(selectedDataFromOtherChart)
    {
        var selectedNamesArray = getSelectedNames(selectedDataFromOtherChart);
        paintPath(selectedNamesArray);
    }


    //---------------------------------------------------------------------------
    function paintPath( exludeList )
    {

        var pathMainList = svg.selectAll(".rect-background");
        var pathList = pathMainList[0];


        for ( var cnt = 0; cnt < pathList.length; cnt++)
        {
            var path = pathList[cnt];
            var pathId = d3.select(path).attr("id");
            //var pathIdOne = d3.select(path).attr("idone");

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

       /* console.log("*************");
        console.log(globalLegend);*/
        var selectedNamesArray = [];
        for ( cnt = 0; cnt <  selectedDataFromOtherChart.length; cnt++)
        {


            var entry0 = "";
            var entry = globalLegend[cnt];
            if (typeof entry !== "undefined") {



            entry0 = entry.cluster;

           }


           var entry1 = "";
           if (typeof entry !== "undefined") {



            entry1 =  entry.state;

           }






            var point = selectedDataFromOtherChart[cnt];
            //alert(point[0]);

            /*if (  IsNumeric(point[0].split(" ").join("_")) ||  IsNumeric(point[1].split(" ").join("_"))     ){

                selectedNamesArray.push("IDPREFIX_" + point[0].split(" ").join("_") + point[1].split(" ").join("_"));

            }
            else{

                selectedNamesArray.push("IDPREFIX_" + point[0].split(" ").join("_") + point[1].split(" ").join("_"));
            }*/




            selectedNamesArray.push("IDPREFIX_" + point[0].split(" ").join("_") + point[1].split(" ").join("_"));


        }
        //globelLegend = [];
        return selectedNamesArray;
    }

    //---------------------------------------------------------------------------
    function getOriginalColor( countryName )
    {
        //alert(countryName);

        for ( var cnt = 0; cnt < globalLegend.length; cnt ++ )
        {
            var entry = globalLegend[cnt];
            /*console.log("entryyyy");
            console.log(entry);*/

            var completeName = "IDPREFIX_" + entry.cluster + entry.state;
            /*console.log("founnd");
            console.log(completeName);*/

            if ( completeName.split(" ").join("_") == countryName.split(" ").join("_") )
            {
                return entry.color;
            }
        }

        return "#cccccc";
    }


    //---------------------------------------------------------------------------






//---------------------------------------------------------------------------




"""}
    results={'code':'', 'errors':[]}

    def __init__(self, mappingInfoForDimension, mappingIngfoForMeasure,  mappingInfoForValue, chartrowIndex):
        self.mappingInfoDimension=mappingInfoForDimension
        self.mappingInfoMeasure=mappingIngfoForMeasure

        self.mappingInfoValue=mappingInfoForValue
        self.chartRoxIndex = chartrowIndex
        self.results={'code':'', 'errors': []}

    def transform(self):
        try:
            code=""
            parallelcoordinatesGeneratorRows={}
            parallelcoordinatesGeneratorRowsArray = []
            xEntries = []


            firstDim = self.mappingInfoDimension[0]['label']





            indexXAxis = self.getDimensionIndex( "x-Axis")
            indexForXAxis = indexXAxis['ind']
            labelXAxis = indexXAxis['label']


            indexBarAxis = self.getDimensionIndex( "Bar")

            indexForBarAxis = indexBarAxis['ind']
            labelBar = indexXAxis['label']

            for element in self.mappingInfoValue:
                xAxisLabel = element['observation']['dimensionlabel%s'%(indexForXAxis)]
                labelForYAxis = element['observation']['dimensionlabel%s'%(indexForBarAxis)]


                elementForYAxisArray=[]
                elementForXAxis=xAxisLabel
                elementForYAxis = element['observation']['measurevalue%s'%0]

                labelYAxis = self.mappingInfoMeasure[0]['label']


                if not elementForYAxis:
                        elementForYAxis = str(0.0)

                bol = self.isReal(elementForYAxis)

                if not bol:
                    elementForYAxis = str(0.0)


                valueObj = { labelForYAxis : elementForYAxis }
                if elementForXAxis in parallelcoordinatesGeneratorRows:
                    parallelcoordinatesGeneratorRows[elementForXAxis].append(valueObj)
                else:
                    parallelcoordinatesGeneratorRows[elementForXAxis] =  elementForYAxisArray
                    parallelcoordinatesGeneratorRows[elementForXAxis].append(valueObj)

                xEntries.append(labelForYAxis)


            xEntries = self.unique(xEntries)

            strResult = "[ "
            for element in parallelcoordinatesGeneratorRows:
                values = parallelcoordinatesGeneratorRows[ element ]
                values.sort()

                strValueObject = ""

                strContent = ""
                valueKeys = []
                for value in values:
                    for key in value.keys():
                        valueKeys.append(key)

                        strContent = strContent + '"'+key+'"'+":" + value[key]+","

                strContent = strContent  + '"State": '+ '"'+element+'",'  + '"id": '+ '"'+labelXAxis+'",'

                for xValue in xEntries:
                    if xValue in valueKeys:
                        strContent = strContent
                    else:
                        strContent = strContent + '"'+xValue+'"'+":0.0,"



                tempList = list(strContent)
                tempList[len(tempList)-1]=""
                strEndContent = "".join(tempList)

                strValueObject = "{" +strContent+ "}, "
                toDictObject = strValueObject
                strResult = strResult + toDictObject


            tempList = list(strResult)
            tempList[len(tempList)-2]=""
            strEndResult = "".join(tempList)
            strResult = strEndResult + "]"



            code = self.codeObject['code']
            code = code.replace ("@@@LABEL@@@", labelXAxis)
            code = code.replace ("@@@LABELY@@@", labelYAxis)
            code = code.replace("@@@CHARTROWINDEX@@@", self.chartRoxIndex )
            code = code.replace("@@@FIRSTDIM@@@", firstDim )
            code = code.replace("@@@DATA@@@", "".join(strResult))

            self.results['code']=code

            print strResult
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


    def getDimensionIndex(self, channelName):
        mappedDimensionIndex = ""
        xAxisDimension = ""

        mappedDimensionUri = ""
        mappedDimensionLabel = ""
        for clientObj in self.mappingInfoDimension:

            cubeComponent = clientObj['cubecomponent']
            if cubeComponent == channelName:
                mappedDimensionUri = clientObj['dimensionuri']

                mappedDimensionLabel = clientObj['label']
                mappedDimensionIndex = clientObj['index']

                mappedObject = {'label': mappedDimensionLabel, 'ind' : mappedDimensionIndex}

                return mappedObject


    def getDimensionIndex2(self, channelName, indexForXAxis,  indexForLineAxis):

        xAxis = self.mappingInfoDimension[indexForXAxis]['index']
        dimForXAxis = self.mappingInfoDimension[indexForXAxis]['dimensionuri']

        lineAxis = self.mappingInfoDimension[indexForLineAxis]['index']
        dimForLineAxis = self.mappingInfoDimension[indexForLineAxis]['dimensionuri']



        for clientObj in self.mappingInfoDimension:
            cubeComponent = clientObj['cubecomponent']
            if cubeComponent == channelName:
                mappedDimensionUri = clientObj['dimensionuri']
                mappedDimensionLabel = clientObj['label']

                mappedDimensionIndex = clientObj['index']
                if (mappedDimensionUri != dimForXAxis and mappedDimensionUri != dimForLineAxis ):
                    if (mappedDimensionIndex != xAxis and mappedDimensionIndex!= lineAxis ):


                        return mappedDimensionIndex

    def isReal(self, txt):
        try:
            float(txt)
            return True
        except ValueError:
            return False
