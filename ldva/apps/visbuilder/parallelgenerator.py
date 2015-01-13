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
import re

from operator import itemgetter, attrgetter
from ldva.libs.sparql.utils import SPARQLQuery
from django.utils import simplejson

class ParallelGenerator(generator.Generator):


    mappingInfoDimension = None
    mappingInfoMeasure = None
    dimensions = None

    codeObjectTwo= {'code': """var loc=config.location; function drawParallelCoordinates() {
window.requestAnimFrame = (function(){
  return window.requestAnimationFrame       ||
         window.webkitRequestAnimationFrame ||
         window.mozRequestAnimationFrame    ||
         window.oRequestAnimationFrame      ||
         window.msRequestAnimationFrame     ||
         function( callback ){
           window.setTimeout(callback, 1000 / 60);
         };
})();

var m = [30, 30, 30, 10],
    w = 850 - m[1] - m[3],
    h = 500 - m[0] - m[2];

var x = d3.scale.ordinal().rangePoints([0, w], 1),
    y = {};

var chartRoxIndex = @@@CHARTROWINDEX@@@;
var data = @@@DATA@@@;
var messLabel = @@@MESSLABEL@@@;
//var colors = d3.scale.category20();
var colArray = @@@COLOR@@@;

var firstDim = @@@FIRSTDIM@@@;
var tableForDimArray = @@@TABLEFORDIMARRAY@@@;
var tableForMesArray = @@@TABLEFORMESARRAY@@@;

function getUriFromLabel(label){
    for (var i=0; i<tableForDimArray.length; i++)
        if (tableForDimArray[i].label == label)
            return tableForDimArray[i].dimension;
    for (var i=0; i<tableForMesArray.length; i++)
        if (tableForMesArray[i].label == label)
            return tableForMesArray[i].measure;
}

var col = d3.scale.category20();
var strg = {};

for (var j = 0; j<colArray.length; j++){
    var label = colArray[j];


    var clr = col(j);

    strg[label] = clr;

}

var colors = strg;
//console.log(colors);
var $loc = $("#"+loc);
$loc.append('<canvas id="2'+loc+'" class="background" style="position:relative;"></canvas><canvas id="3'+loc+'" class="foreground" style="position: absolute; top: 0; left: 0;"></canvas>');

//d3.selectAll("#"+loc+" "+"2"+loc)

//console.log($loc.find("#2"+loc));

var canvasStyle = m.join("px ") + "px";


//make canvas update independent (just consider local canvas)

d3.selectAll('canvas').each(function(d,i) {
                 //console.log(this);
             if ( this.id == ("2"+loc) || this.id == ("3"+loc) )
             {
                 var selection = d3.select(this);
                 //alert ("nur meine canvas (nicht andere): "+this.id);
                 selection.attr("width", w + m[1] + m[3])
                 .attr("height", h + m[0] + m[2])
                 .style("padding", canvasStyle);
             }
         });





//foreground = $loc.find('.foreground')[0].getContext('2d');
foreground = $loc.find("#3"+loc)[0].getContext('2d');

//alert("FORE ID: "+ foreground);
foreground.strokeStyle = "rgba(0,100,160,0.1)";

var svg = d3.select("#"+loc).append("svg:svg")
    .style("position", "absolute")
    .style("top", "0")

    .style("left", "0")
    .attr("width", w + m[1] + m[3])
    .attr("height", h + m[0] + m[2])
  .append("svg:g")
    .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

// Could value belong to a quantitative ordinal scale
var quant_p = function(v){return (parseFloat(v) == v) || (v == "")};

/*d3.csv("nutrients.csv", function(data) {
  //Reduce the number of unique names... their were > 7K.
  data.forEach(function(d){d["name"] = d["name"].slice(0,1);});*/

  // Extract the list of dimensions.
  dimensions = d3.keys(data[0]).slice(1).concat(d3.keys(data[0]).slice(0,1)); //Put the ordinal dimensions on opposite sides of the chart for easier viewing
  x.domain(dimensions);


  //console.log(dimensions);
  var line = d3.svg.line(),
    axis = d3.svg.axis().orient("left"),
    foreground,
    dimensions,
    brush_count = 0;

  // Create a scale for each.
 dimensions.forEach(function(d) {
    var vals = data.map(function(p) {return p[d];});
    ///console.log(vals);
    //if (vals.every(quant_p) && vals >=2003 && vals <=2008){
    if (vals.every(quant_p) && d !== "Year" && d!== "Reference Period" && d!="Score"  && d!="Source" && d!== "year"){
      y[d] = d3.scale.linear()
          .domain(d3.extent(vals.map(function(p){return +p})))
          .range([h, 0]);}
    else{

      y[d] = d3.scale.ordinal()
          .domain(vals.filter(function(v, i) {return vals.indexOf(v) == i;}).sort())
          .rangePoints([h, 0],1);}
  })

  /*dimensions.forEach(function(d) {
    var vals = data.map(function(p) {return p[d];});
    if ( vals >=2003 && vals <=2008){
    //console.log(vals);
        y[d] = d3.scale.ordinal()
          .domain(vals.filter(function(v, i) {return vals.indexOf(v) == i;}).sort(d3.ascending))
          .rangePoints([h, 0],1);}

    else if (vals.every(quant_p)){
      y[d] = d3.scale.linear()
          .domain(d3.extent(vals.map(function(p){return +p})))
          .range([h, 0]);}
    else{

      y[d] = d3.scale.ordinal()
          .domain(vals.filter(function(v, i) {return vals.indexOf(v) == i;}).sort())
          .rangePoints([h, 0],1);}
  })*/




  // Render full foreground
  paths(data, foreground, brush_count);
  var selektiert = [];
  var selektierteIndex = 0;

  var selektierte = {  };

  // Add a group element for each dimension.
  var g = svg.selectAll(".dimension")
      .data(dimensions)
    .enter().append("svg:g")
      .attr("class", "dimension")
      .attr("id", function(d) {return "IDPREFIX_" + d.split(" ").join("_"); })
      .attr("transform", function(d) { return "translate(" + x(d) + ")"; });



  // Add an axis and title.
  g.append("svg:g")
      .attr("class", "axis")
      .each(function(d) { d3.select(this).call(axis.scale(y[d])); })
      .append("svg:text")
      .attr("text-anchor", "middle")
      .attr("y", -9)
      .text(String).attr("class", "label")
      .each(function(d) { selektierte[d] = this; d3.select(this).on('click', function(x){
                Vis.view.getNewAxisLabel(d, function(newAxisLabel){ (d3.select(selektierte[d]).text());d3.select(selektierte[d]).text(newAxisLabel); });
            });

             });

  // Add and store a brush for each axis.
  g.append("svg:g")
      .attr("class", "brush")
      .each(function(d) {
          //console.log(d);
          d3.select(this).call(
              y[d].brush = d3.svg.brush().y(y[d])
                  .on("brush", brush)
                  .on("brushend", brushend)
          );
      })
    .selectAll("rect")
      .attr("x", -12)
      .attr("width", 24);

  // Handles a brush event, toggling the display of foreground lines.
  function brush() {


    brush_count++;
    var actives = dimensions.filter(function(p) { return !y[p].brush.empty(); }),
        extents = actives.map(function(p) { return y[p].brush.extent(); });


    // Get lines within extents
    var selected = [];
    var selected2 = [];


    data.map(function(d) {
      return actives.every(function(p, i) {
        var p_new = (y[p].ticks)?d[p]:y[p](d[p]); //convert to pixel range if ordinal

          //console.log(d);
          return extents[i][0] <= p_new && p_new <= extents[i][1];
      }) ? selected.push(d) : null;
    });

    // Render selected lines
    foreground.clearRect(0,0,w+1,h+1);
    /*console.log(foreground);
    alert(brush_count);*/
    paths(selected, foreground, brush_count);



  }

//---------------------------------------------------------------------

   // Handles a brush event, toggling the display of foreground lines.
  function brushend() {

    var compledData = [];
    var selectedDimensions = [];

    brush_count++;
    var actives = dimensions.filter(function(p) { return !y[p].brush.empty(); }),
        extents = actives.map(function(p) { return y[p].brush.extent(); });

    //console.log("Extends: ");
    //console.log(extents);
    //console.log(extents.length);

     // Get lines within extents
    var selected = [];
    var selected2 = [];

    data.map(function(d) {
      return actives.every(function(p, i) {
        var p_new = (y[p].ticks)?d[p]:y[p](d[p]); //convert to pixel range if ordinal

          //console.log(d);
          return extents[i][0] <= p_new && p_new <= extents[i][1];
      }) ? selected.push(d) : null;
    });

    // over-dataset-brushing for ordinal values
    // actives = brushedLabels
    for (var e =0; e<actives.length; e++){
        var aBrushedAxisLabel = actives[e];
        if (y[aBrushedAxisLabel].ticks){
            var extendFrom = extents[e][0];
            var extendTo = extents[e][1];
            //console.log('from-to: ' + extendFrom + ' ' + extendFrom);
            var selectedDimension = {
                from:extendFrom,
                to: extendTo,
                label: aBrushedAxisLabel,
                uri: getUriFromLabel(aBrushedAxisLabel)
            };
            selectedDimensions.push(selectedDimension);
            //console.log(selectedDimension);
        }
    }

    // Render selected lines
    foreground.clearRect(0,0,w+1,h+1);
    paths(selected, foreground, brush_count);

    //console.log("------DA------");
    //console.log(selected);
    //strgStream = getSelectedData( selected);


    if (extents.length == 0) {
        brushingObserver.updateEmpty(chartRoxIndex);
    } else {
        selected = prepareData(selected);
        compledData = getSelectedData(selected);
        brushingObserver.update(chartRoxIndex, compledData);
    }

  }


 //----------------------------------------------------------------

  function getSelectedData(selected){
 //console.log(selected);



    var compledData2 = [];

    for (var i = 0; i< selected.length; i++ ){
        var selectedObject =  selected[i];
        //alert(selectedObject);
        var compledData = [];
        for (var j = 0; j<selectedObject.length; j++ ){
          //alert(selectedObject);
            var selectedEntry = selectedObject[j];
            var entry = "" ;

            for (var k= 0; k<selectedEntry.length ; k++){
              //alert(selectedObject);
                entry = selectedEntry[k];
                 if (IsNumeric(entry) && entry <=1980 || entry >=2014){
                     entry =  parseFloat(entry);
                 }
                compledData.push(entry);


            }

        }

        compledData2.push(compledData);

    }


    //console.log(compledData2);
    return compledData2;
}



 //--------------------------------------------------------------------

 function prepareData (strgStream){
    //console.log(firstDim);
    var newArray = [];
     var dim2  = "";
     var myArray = [];
     for (var i = 0; i< strgStream.length; i++){

        var valNewObject = "";
              for (var k = 0 ; k<messLabel.length; k++){
                   var value = messLabel[k];
                   valNewObject = valNewObject+ parseFloat(strgStream[i][value]) + ", "  ;
                    var dimNewObject = "";
                    //console.log(firstDim);
                    for (var j = 0; j< firstDim.length; j++){
                          var dim = firstDim[j].label.split(' ').join('');

                          var strgStr = strgStream[i][dim];
                          var strgStr = strgStr.split('/').join(',');

                          dimNewObject = dimNewObject+ strgStr+ ","  ;



             }

         }
         dimNewObjectNew = dimNewObject.substring(0, dimNewObject.length-1);
         myArray = listToArray(dimNewObject, ',');
         myArray2 = listToArray(valNewObject, ',');






      newArray.push([myArray, myArray2]);
    }


  //console.log(newArray);
 return (newArray);

  }

  //-----------------------------------------------------
  function listToArray(fullString, separator) {


  var fullArray = [];

  if (fullString !== undefined) {


    if (fullString.indexOf(separator) == -1) {
      fullAray.push(fullString);
    } else {

      fullArray = fullString.split(separator);
    }
  }

fullArrayNew =  fullArray.splice(fullArray.length-1, 1);
return fullArray;
}


//-----------------------------------------------------------------------------

function IsNumeric(input)
{
    return (input - 0) == input && (input+'').replace(/^\s+|\s+$/g, "").length > 0;
}



//----------------------------------------------------------------------------

//var selectedData = [{'Country':'Bulgaria', 'Value': '0.6852', 'Year':'2009'}, {'Year': '2009', 'Value': '0.2151', 'Country': 'Cyprus'}];
 //foreground.clearRect(0,0,w+1,h+1);
 //paths(selectedData, foreground, 0  );



brushingObserver.registerListener(function(newChartRowIndex){ chartRowIndex = newChartRowIndex; }, chartRoxIndex, function(selectedData){
    //console.log(selectedData);

    svg.selectAll('.brush')
        .each(function(d) {
              d3.select(this).call(
                  y[d].brush = d3.svg.brush().y(y[d])
                      .on("brush", brush)
                      .on("brushend", brushend)
              );
          })
        .selectAll("rect")
          .attr("x", -12)
          .attr("width", 24);

    //svg.selectAll('.brush').call(brush);
    //console.log('messss');
    //console.log(messLabel.length);

    /*if(selectedData == null){    // DON'T PUT IT. IT DOES NOT WORK. ASK ME !!! I HAT THE SAME IMPLEMENTATION HER BEVOR I FIGURE OUT, THAT IT DOES NOT WORK
        paths(data, foreground, brush_count);
        return;
    }*/

     var dataArrayFirst = [];

  if(selectedData)
     for (var i = 0; i<selectedData.length; i++){
         var selectData = selectedData[i];
         /*console.log('##############');
         console.log(selectData);*/


         var l  = 0;
        var entityObject = {};
         for (l = 0; l<firstDim.length; l++){
             var dime = (firstDim[l].label).split(' ').join('');
             var entity = "";

             entityObject[dime] = selectData[l];
             //console.log(entityObject);

             for (var g = 0; g<messLabel.length;g ++){
                 var value = (messLabel[g]);
                 entityObject[value] = String(selectData[l+1]);


             }

        }
        dataArrayFirst.push((entityObject));
           foreground.clearRect(0,0,w+1,h+1);
    paths(dataArrayFirst, foreground,20  );

      //console.log(entityObject);

     //dataArraySecond.push(dataArrayFirst);


 }



}, function(selectedDimensions){

    var selected = [];
    //console.log("selectedDimensions: ");
    //console.log(selectedDimensions);
    //console.log(data);
    //console.log(tableForDimArray);
    //console.log(tableForMesArray);

    if (selectedDimensions == null){
        foreground.clearRect(0,0,w+1,h+1);
        paths(data, foreground, brush_count);
        return;
    }

    data.map(function(d) {
        var isSelected = true;
        for(var i=0; i<selectedDimensions.length; i++){
            var isSelectedDimension = false;
            for(var j=0; j<tableForDimArray.length; j++){
                if (tableForDimArray[j].dimension == selectedDimensions[i].uri){
                    var value = d[tableForDimArray[j].label];
                    if (selectedDimensions[i].from != null && selectedDimensions[i].from <= value && selectedDimensions[i].to >= value)
                        isSelectedDimension = true;
                    else if (selectedDimensions[i].values != null && _.contains(selectedDimensions[i].values, value))
                        isSelectedDimension = true;
                }
            }
            for(var j=0; j<tableForMesArray.length; j++){
                if (tableForMesArray[j].measure == selectedDimensions[i].uri){
                    var value = d[tableForMesArray[j].label];
                    if (isNumber(value))
                        value = value*1;
                    if (selectedDimensions[i].from != null && selectedDimensions[i].from <= value && selectedDimensions[i].to >= value)
                        isSelectedDimension = true;
                    else if (selectedDimensions[i].values != null && _.contains(selectedDimensions[i].values, value))
                        isSelectedDimension = true;
                }
            }
            if (!isSelectedDimension)
                isSelected = false;
            //if (isSelectedDimension)
            //    isSelected = true;
        }
        if (isSelected)
            selected.push(d);
    });

    // Render selected lines
    foreground.clearRect(0,0,w+1,h+1);
    paths(selected, foreground, brush_count);
});



//----------------------------------------------------------------------------------------------------

function paths(data, ctx, count) {
 /*console.log('path');
    console.log(data);
    console.log(brush_count);
     console.log(ctx);*/

    var n = data.length,
        i = 0,
        reset = false;


    function render() {
      var max = d3.min([i+60, n]);
      data.slice(i,max).forEach(function(d) {
      //console.log(d);
        path(d, foreground, @@@LAB@@@);

      });
      i = max;
    };
    (function animloop(){
      /*console.log('count '+ count)
      console.log('brush_count' + brush_count )*/
      if (i >= n ) return;
      requestAnimFrame(animloop);
      render();
    })();
  };



function path(d, ctx, color) {


  if (color) ctx.strokeStyle = color;
  ctx.beginPath();
  dimensions.map(function(p,i) {
    if (i == 0) {
      ctx.moveTo(x(p),y[p](d[p]));
    } else {
      ctx.lineTo(x(p),y[p](d[p]));
    }
  });
  ctx.stroke();
};
}
drawParallelCoordinates()
 """}


    def __init__(self, mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue, dataset, chartrowIndex):
        self.mappingInfoDimension = mappingInfoForDimension
        self.mappingInfoMeasure = mappingIngfoForMeasure
        self.mappingInfoValue = mappingInfoForValue

        self.chartRoxIndex = chartrowIndex
        self.dataset = dataset
        self.results = {'code':'', 'errors': [], 'mappinginfo': {}}
    def transform(self):
        try:
            self.results =  {}
            code = self.codeObjectTwo['code']
            tableForDim = {}


            tableForMeasure = {}
            tableForDimArray= []



            indexArrayColor = self.getDimensionIndex('Color')
            indexForColor = indexArrayColor[0]['index']
            labelForColor = indexArrayColor[0]['label']


            for entry in self.mappingInfoDimension:
                dim = entry['dimensionuri']
                dimLabel = entry['label']
                dimLabel = dimLabel.replace(' ', '')
                tableForDim = {'dimension' : '', 'label': ''}

                tableForDim['dimension'] = dim
                tableForDim['label'] = dimLabel
                tableForDimArray.append(tableForDim)


            tableForMesArray = []
            labelArray = []
            for meas in self.mappingInfoMeasure:
                value = meas ['measureuri']
                label = meas ['label']
                labelArray.append(label)


                tableForMeasure = {'measure' : '', 'label': ''}
                tableForMeasure ['measure'] = value
                tableForMeasure ['label'] = label

                tableForMesArray.append (tableForMeasure)

            lengtArray = []
            parallelcoordinatesGeneratorRowsArray = []
            for i in range(len(tableForDimArray)):
                label = tableForDimArray[i]['label']
                dim = 'dimensionlabel%s'% (i)

                xAxisArray = []
                parallelcoordinatesGeneratorRows = {}
                for element in self.mappingInfoValue:
                    xAxis = element['observation'][dim]
                    if dim in parallelcoordinatesGeneratorRows:
                        parallelcoordinatesGeneratorRows[dim].append(xAxis)
                    else:
                            parallelcoordinatesGeneratorRows[dim] =  xAxisArray
                            parallelcoordinatesGeneratorRows[dim].append(xAxis)

                parallelcoordinatesGeneratorRowsArray.append(parallelcoordinatesGeneratorRows)


            entitiesArray = []
            for i in range(len(parallelcoordinatesGeneratorRowsArray)):
                entities = parallelcoordinatesGeneratorRowsArray[i]['dimensionlabel%s'% (i)]
                entities = self.unique(entities)

                lengOfDim = len(entities)
                entitiesObject = {'index': i, 'entity': entities, 'length':lengOfDim }
                entitiesArray.append(entitiesObject)


            findLabel = ""
            findIndex = ""
            maxLength = 0
            for k in entitiesArray:
                if k['length']> maxLength:
                    maxLength = k['length']
                    findIndex = k['index']
                    findLabel = tableForDimArray[findIndex]['label']


            colorArray = []
            for element in self.mappingInfoValue:
                color = element['observation']['dimensionlabel%s'% (indexForColor)]
                colorArray.append(color)

            strResult = "[ "
            xAxisArray = []
            for element in self.mappingInfoValue:
                strg = ""
                for i in range(len(tableForDimArray)):
                    xAxis = element['observation']['dimensionlabel%s'% (i)]
                    label2 = tableForDimArray[i]['label']
                    strg = strg + '"'+label2+'":"'+xAxis+'",'

                strg2 = ""
                for j in range(len(tableForMesArray)):
                    labelForValue = tableForMesArray[j]['label']
                    yAxis = element['observation']['measurevalue%s'%(j)]
                    if not yAxis:
                        yAxis = str(0.0)
                    bol = self.isReal(yAxis)
                    if not bol:
                        yAxis = str(0.0)
                    strg2 = strg2 + '"' + labelForValue + '":"'+ yAxis+'",'

                strg3 = strg + strg2
                '''tempList1 = list(strg2)
                tempList1[len(tempList1)-1]=""
                strEndContent1 = "".join(tempList1)'''

                strValueObject = "{" +strg3+ "}, "
                toDictObject = strValueObject
                strResult = strResult + toDictObject

            tempList = list(strResult)
            tempList[len(tempList)-2]=""
            strEndResult = "".join(tempList)

            strResult = strEndResult + "]"

            code=code.replace("@@@DATA@@@", "".join(strResult))
            code = code.replace("@@@COLOR@@@", simplejson.dumps((colorArray)))

            code = code.replace("@@@MESSLABEL@@@", simplejson.dumps((labelArray)))
            code = code.replace("@@@CHARTROWINDEX@@@", self.chartRoxIndex )
            code = code.replace("@@@FIRSTDIM@@@", simplejson.dumps((self.mappingInfoDimension )))
            code = code.replace("@@@TABLEFORMESARRAY@@@", simplejson.dumps(tableForMesArray))
            code = code.replace("@@@TABLEFORDIMARRAY@@@", simplejson.dumps(tableForDimArray))


            labForClr = "colors[d."+labelForColor.replace(" ", "")+"]"
            code = code.replace("@@@LAB@@@", (labForClr))

            self.results['code']=code


        except Exception as ex:
            raise Exception("-ParallelGeneratorOne.transform: %s"%ex)

    def unique(self, items):
        found = []
        keep = []

        for item in items:
            if item not in found:
                found.append(item)
                keep.append(item)

        return keep


    def isReal(self, txt):
        try:
            float(txt)
            return True
        except ValueError:
            return False


    def getDimensionIndex(self, channelName):
        mappedDimensionIndexArray = []

        mappedDimensionUriArray = []
        mappedDimensionLabelArray = []
        for clientObj in self.mappingInfoDimension:
            cubeComponent = clientObj['cubecomponent']
            if cubeComponent == channelName:
                mappedDimensionUri = clientObj['dimensionuri']

                label = clientObj['label']
                index = clientObj['index']

                newObject = {'label': label, 'index': index, 'uri':mappedDimensionUri }
                mappedDimensionIndexArray.append( newObject)

        return mappedDimensionIndexArray


