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
    
    codeObjectTwo= {'code': """var loc=config.location;function drawParallelCoordinates() {
var m = [30, 30, 30, 10],
    w = 960 - m[1] - m[3],
    h = 500 - m[0] - m[2];

var x = d3.scale.ordinal().rangePoints([0, w], 1),
    y = {};

var line = d3.svg.line(),
    axis = d3.svg.axis().orient("left"),
    background,
    foreground;

d3.selectAll("canvas")
    .attr("width", w + m[1] + m[3])
    .attr("height", h + m[0] + m[2])
    .style("padding", m.join("px ") + "px");

foreground = document.getElementById('foreground').getContext('2d');
background = document.getElementById('background').getContext('2d');

foreground.strokeStyle = "rgba(0,100,160,0.24)";
background.strokeStyle = "rgba(0,0,0,0.02)";

var svg = d3.select("#"+loc).append("svg:svg")
    .attr("width", w + m[1] + m[3])
    .attr("height", h + m[0] + m[2])
  .append("svg:g")
    .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

var cars = @@@DATA@@@;
var lines = @@@LINE@@@;


  // Extract the list of dimensions and create a scale for each.
  x.domain(dimensions = d3.keys(cars[0]).filter(function(d) {
  //console.log(d);
  if (d === "name") return false;
        else if (d === "Year") {
            
                y[d] = d3.scale.ordinal()
                
                    .domain(cars.map(function (p) {
                    
                    return p[d];
                }))
                //.range()
                //.range(["brown", "#999", "#999", "steelblue"])
                  

                    .rangePoints([h, 0]);
           

        } else if (d === "Labels") {
            y[d] = d3.scale.ordinal()
                .domain(cars.map(function (p) {
                return p[d];
            }))

                .rangePoints([h, 0]);

        } else {
            y[d] = d3.scale.linear()


                .domain(d3.extent(cars, function (p)

            {
                //console.log(p[d]);
                return +p[d];
            }))
                .range([h, 0]);

        }
        
        return true;
        //console.log(p[d]);
    }));

  // Render full foreground and background
  cars.map(function(d) {
    path(d, background);
    

    var randomRedColor = getRandomInt(0,255);
    var randomGreenColor = getRandomInt(0,255);
    var randomBlueColor = getRandomInt(0,255);
    foreground.strokeStyle = "rgba("+randomRedColor+", "+randomGreenColor+", "+randomBlueColor+", 1)";
    path(d, foreground);
    
  });

  // Add a group element for each dimension.
  var g = svg.selectAll(".dimension")
      .data(dimensions)
    .enter().append("svg:g")
      .attr("class", "dimension")
      .attr("transform", function(d) { return "translate(" + x(d) + ")"; });

  // Add an axis and title.
  g.append("svg:g")
      .attr("class", "axis")
      .each(function(d) { d3.select(this).call(axis.scale(y[d])); })
    .append("svg:text")
      .attr("text-anchor", "middle")
      .attr("y", -9)
      .text(String);

  // Add and store a brush for each axis.
  g.append("svg:g")
      .attr("class", "brush")
      .each(function(d) { d3.select(this).call(y[d].brush = d3.svg.brush().y(y[d]).on("brush", brush)); })
    .selectAll("rect")
      .attr("x", -8)
      .attr("width", 16);
//console.log(g);
  // Handles a brush event, toggling the display of foreground lines.
  function brush() {
    var actives = dimensions.filter(function(p) { return !y[p].brush.empty(); }),
        extents = actives.map(function(p) { return y[p].brush.extent(); });

    // Get lines within extents
    var selected = [];
    cars.map(function(d) {
      return actives.every(function(p, i) {
        return extents[i][0] <= d[p] && d[p] <= extents[i][1];
      }) ? selected.push(d) : null;
    });

    // Render selected lines
    foreground.clearRect(0,0,w+1,h+1);
    selected.map(function(d) {
      path(d, foreground);
    });
  }

function getRandomInt (min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function path(d, ctx) {
  ctx.beginPath();
 
  dimensions.map(function(p,i) {
  //console.log(i);
    if (i == 0) {
        
      ctx.moveTo(x(p),y[p](d[p]));
    } else { 
      ctx.lineTo(x(p),y[p](d[p]));
      
    }
  });
  ctx.stroke();
  
  //console.log(dimensions);
 

  
};
}

function drawLegend(selectDataArray, header, body){
    var metricAscending = true;
    var nameAscending = true;
    

    d3.select(header).html(null);
    var outerTable = d3.select(header).append("div").attr("id","treger");
    var tabelle = outerTable.append("table");
    var columns = ["Legend"];
        
    tabelle.attr("cellpadding", 0).attr("border", 0).attr("cellspacing", 0).attr("width", "100%").attr("align", "center").append("thead").append("tr").selectAll("th").data(columns).enter()
    .append("th").attr("bgcolor", "#cccccc").attr("width", "67%").attr("align", "left")
    .text(function (column) {  return column; })
    .on("click", function (d) {

    });

    var underTable = d3.select(body).append("div").attr("id","treger2").append("table");
    underTable.attr("border", 0)
    underTable.attr("cellpadding", 0).attr("border", 0).attr("cellspacing", 0).attr("width", "100%").attr("align", "center");
    
    var tbody = underTable.append("tbody");
    var rows = tbody.selectAll("tr").data(selectDataArray).enter().append("tr")//.sort(sortValueDescending);

    var td = rows.selectAll("td")
      .data(function(d){ return d3.values(d)})
      .enter().append("td").attr("align", "left").attr("width", "70%")
      .html(function(d) {return d})

}
drawParallelCoordinates() ;  
 """}
    
    
    
    
    
    
    
    codeObject = {'code': """var loc=config.location; 
var globalColorCounter = 0;
var globalColorCount = 0; 


var cars = @@@DATA@@@;
var lines = @@@LINE@@@;

function drawParallelCoordinates() {
var m = [30, 30, 30, 10],
    w = 960 - m[1] - m[3],
    h = 500 - m[0] - m[2];

var x = d3.scale.ordinal().rangePoints([0, w], 1),
    y = {};

var line = d3.svg.line(),
    axis = d3.svg.axis().orient("left"),
    background,
    foreground;



d3.selectAll("canvas")
    .attr("width", w + m[1] + m[3])
    .attr("height", h + m[0] + m[2])
    .style("padding", m.join("px ") + "px");

foreground = document.getElementById('foreground').getContext('2d');
background = document.getElementById('background').getContext('2d');

foreground.strokeStyle = "rgba(0,100,160,0.24)";
background.strokeStyle = "rgba(0,0,0,0.02)";

var svg =  d3.select("#"+loc).append("svg:svg")
    .attr("width", w + m[1] + m[3])
    .attr("height", h + m[0] + m[2])
  .append("svg:g")
    .attr("transform", "translate(" + m[3] + "," + m[0] + ")");


  // Extract the list of dimensions and create a scale for each.
  x.domain(dimensions = d3.keys(cars[0]).filter(function(d) {

  if (d === "name") return false;

        else if (d === "Year") {
            
                y[d] = d3.scale.ordinal()
                
                    .domain(cars.map(function (p) {
                      
                    return p[d];
                }))
                //.range()
                //.range(["brown", "#999", "#999", "steelblue"])
                  

                    .rangePoints([h, 0]);
           

        } else if (d === "Labels") {
            y[d] = d3.scale.ordinal()
                .domain(cars.map(function (p) {
                return p[d];
            }))

                .rangePoints([h, 0]);

        } else {
            y[d] = d3.scale.linear()


                .domain(d3.extent(cars, function (p)

            {
                //console.log(p[d]);
                return +p[d];
            }))
                .range([h, 0]);

        }
        
        return true;
        //console.log(p[d]);
    }));

  // Render full foreground and background
  cars.map(function(d) {
    path(d, background);
    
    var colorObj = getColor();
    
    var randomRedColor = colorObj.red;
    var randomGreenColor = colorObj.green;
    var randomBlueColor = colorObj.blue;
    foreground.strokeStyle = "rgba("+randomRedColor+", "+randomGreenColor+", "+randomBlueColor+", 1)";
    path(d, foreground);
    //var colorText = "<font style=\'background-color: "+foreground.strokeStyle+"\'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT>"
    /*var line = "Year";
            globalLegend.push( {"cluster":line, "color": colorText} ); 
            
    globalLegend = [];*/
  });

  // Add a group element for each dimension.
  var g = svg.selectAll(".dimension")
      .data(dimensions)
    .enter().append("svg:g")
      .attr("class", "dimension")
      .attr("transform", function(d) { return "translate(" + x(d) + ")"; });

  // Add an axis and title.
  g.append("svg:g")
      .attr("class", "axis")
      .each(function(d) { d3.select(this).call(axis.scale(y[d])); })
    .append("svg:text")
      .attr("text-anchor", "middle")
      .attr("y", -9)
      .text(String);

  // Add and store a brush for each axis.
  g.append("svg:g")
      .attr("class", "brush")
      .each(function(d) { d3.select(this).call(y[d].brush = d3.svg.brush().y(y[d]).on("brush", brush)); })
    .selectAll("rect")
      .attr("x", -8)
      .attr("width", 16);
//console.log(g);
  // Handles a brush event, toggling the display of foreground lines.
  function brush() {
    var actives = dimensions.filter(function(p) { return !y[p].brush.empty(); }),
        extents = actives.map(function(p) { return y[p].brush.extent(); });

    // Get lines within extents
    var selected = [];
    cars.map(function(d) {
      return actives.every(function(p, i) {
        return extents[i][0] <= d[p] && d[p] <= extents[i][1];
      }) ? selected.push(d) : null;
    });

    // Render selected lines
    foreground.clearRect(0,0,w+1,h+1);
    selected.map(function(d) {
      path(d, foreground);
    });
  }



function path(d, ctx) {    
  ctx.beginPath();
 
  dimensions.map(function(p,i) {
  //console.log(i);
    if (i == 0) {
        
      ctx.moveTo(x(p),y[p](d[p]));
    } else { 
    
      ctx.lineTo(x(p),y[p](d[p]));
      
    }
  });
  ctx.stroke();

};
}

function drawLegend(selectDataArray, header, body){
    var metricAscending = true;
    var nameAscending = true;
    

    d3.select(header).html(null);
    var outerTable = d3.select(header).append("div").attr("id","treger");
    var tabelle = outerTable.append("table");
    var columns = ["Legend"];
        
    tabelle.attr("cellpadding", 0).attr("border", 0).attr("cellspacing", 0).attr("width", "100%").attr("align", "center").append("thead").append("tr").selectAll("th").data(columns).enter()
    .append("th").attr("bgcolor", "#cccccc").attr("width", "67%").attr("align", "left")
    .text(function (column) {  return column; })
    .on("click", function (d) {

    });

    var underTable = d3.select(body).append("div").attr("id","treger2").append("table");
    underTable.attr("border", 0)
    underTable.attr("cellpadding", 0).attr("border", 0).attr("cellspacing", 0).attr("width", "100%").attr("align", "center");
    
    var tbody = underTable.append("tbody");
    var rows = tbody.selectAll("tr").data(selectDataArray).enter().append("tr")//.sort(sortValueDescending);

    var td = rows.selectAll("td")
      .data(function(d){ return d3.values(d)})
      .enter().append("td").attr("align", "left").attr("width", "70%")
      .html(function(d) {return d})

}

//liefert die Farbe (aufpassen! nicht zufaelling sondern basierend auf anzahl von aufrufen)
function getColor()
{
    var colorObj = {'red': 0, 'green':0, 'blue':0};
    
    var currentIndex = globalColorCounter % globalColorCount;
    
    var keys = [];
    
    for(var j in globalColorMap) 
    {
        //console.log(":: "+j);
        
        colorArray = globalColorMap[j];
        
        colorObj = colorArray[currentIndex];
        break;
    }
    
    ++globalColorCounter;
    return colorObj;
}

//erzeugt ein json in dem alle farben die wir brauchen vorhanden sind
function initColorMap()
{
    
    var keys = [];
    for(var j in cars[0]) keys.push(j);
    
    var len = keys.length;
    
    var allColorMaps = [];
    var candidateColorMap = [];
    //console.log("... "+len);
    for (var k=0; k<len; k++)
    {
        var currentColorMap = getColorMap(k);
        
        allColorMaps.push(currentColorMap);
    }
    
    candidateColorMap = allColorMaps[0];
    for (var k=0; k<allColorMaps.length; k++)
    {
        var currentColorMap = allColorMaps[k];
        
        /*console.log(" VERGLEICH ============================== == ");
        console.log(currentColorMap[d3.keys(currentColorMap)[0]]);
        console.log(" VERGLEICH END============================== == ");*/
        
        if ( currentColorMap[d3.keys(currentColorMap)[0]] )
        {
            if(currentColorMap[d3.keys(currentColorMap)[0]].length>candidateColorMap[d3.keys(candidateColorMap)[0]].length)
            {
                candidateColorMap = currentColorMap;
            }
        }
        
        
    }
    
    globalColorMap = candidateColorMap;
    //global counter init (damit wir wissen wie viele farben es gibt)
    for(var j in globalColorMap) 
    {
        colorArray = globalColorMap[j];
    
        globalColorCount = colorArray.length;
        //console.log("FARBEN: "+globalColorCount);
        break;
    }
    
   
    
    //ok jetzt haben wir farben pro kategorie (zb jahr oder person, egal was)
    printColorMap(globalColorMap);    
    
    //TEST - muss immer gleiche farben fuer gleiche jahren oder personen liefern
    
}
 

 
function getColorMap(index)
{
    var colorMap = [];
    for (var k=0; k<cars.length; k++)
    {
        var oneLine = cars[k];
        var keys = [];
        for(var j in oneLine) keys.push(j);

        var anyDimension = oneLine[keys[index]];
        //console.log("LINE: "+keys+" ==> index: "+keys[index]+", index ist: "+index);
        
        var randomRedColor = getRandomInt(0,255);
        var randomGreenColor = getRandomInt(0,255);
        var randomBlueColor = getRandomInt(0,255);
    
        var colorObj = {'red': randomRedColor, 'green': randomGreenColor, 'blue': randomBlueColor};
        if ( !colorMap[anyDimension] )
        {
            colorMap[anyDimension] = [];
        }
        colorMap[anyDimension].push(colorObj);
    }
    
    return colorMap;
}

function printColorMap(map)
{
    var keys = [];
    //console.log("COLOR MAP: 

    for(var j in map) 
    {
        
        
        colorArray = map[j];
        
        //console.log("K:"+j);
        for (var k in colorArray)
        {
            //console.log("   R: "+colorArray[k].red+", G:"+colorArray[k].green+", B: "+colorArray[k].blue);
        }
    }
}
function getRandomInt (min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}


//zeichnet legend am ende
function drawTheLegend()
{
    globalLegend = [];
    var numOfClusters = globalColorCount;
    
    var keys = [];
    colorArray = [];
    //hole farben fuer erste cluster nur (reicht)
    for(var j in globalColorMap) 
    {
        colorArray = globalColorMap[j];        
        break;
    }
    
    for ( var k=0; k<numOfClusters; k++)
    {
        var colorObj =  colorArray[k];
        var colorText = "<font style=  'background-color: rgb("+colorObj.red+', '+colorObj.green+', '+colorObj.blue+") '>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT>"
        globalLegend.push( {"cluster":lines[k].name, "color":colorText} ); 
    }
    
    drawLegend(globalLegend, "#demo2Up", "#demo2");
    
}


initColorMap();

drawParallelCoordinates() ;

drawTheLegend(); 
"""}
   
    def __init__(self, mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue, dataset):
        self.mappingInfoDimension = mappingInfoForDimension
        
        #print "------------------------------------------------", self.mappingInfoDimension
        self.mappingInfoMeasure = mappingIngfoForMeasure
        #print "------------------------------------------------", self.mappingInfoMeasure
        self.mappingInfoValue = mappingInfoForValue
        print "------------------------------------------------ self.mappingInfoValue", self.mappingInfoValue
        self.dataset = dataset
        self.results = {'code':'', 'errors': [], 'mappinginfo': {}}
        #print "------------------------------------------------", self.mappingInfoValue        
    def transform(self):
        try:  
            self.results =  {}
            lineArraytwo = []           
            labOfdm = ""
            code = self.codeObjectTwo['code']
                     
            tableForDim = {}
            xEntries = []
            tableForDimArray= []
            
            
            for entry in self.mappingInfoDimension:
                dim = entry['dimensionuri']
                tableForDim = {'dimension' : ''}
                
                tableForDim['dimension'] = dim
                tableForDimArray.append(tableForDim)
                #print "DIMMMMMURIIIII",  dim 
                
              
            
            indexForXAxis = self.getDimensionIndex( "x-Axis")
            indexForLineAxis = self.getDimensionIndex( "Line")    
                
            if len(tableForDimArray) == 2:
                lineArray = []
               
                for i in range(len(tableForDimArray)-1):
                    parallelcoordinatesGeneratorRows = {}
                    for element in self.mappingInfoValue:
                        xAxis = element['observation']['dimensionlabel%s'% (indexForXAxis)]  
                        #print "PC#####################################,x-Axis", xAxis
                        line = element['observation']['dimensionlabel%s'% (indexForLineAxis)] 
                        #print "PC#####################################,line", line
                        lineArray.append(line)    
                        yAxisArray = []               
                        elementForXAxis = line
                        yAxis = element['observation']['measurevalue']
                        #print "O:OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOo", yAxis
                        
                        if not yAxis:
                            yAxis = str(0.0)
                        
                        valueObj = { xAxis : yAxis }
                        if elementForXAxis in parallelcoordinatesGeneratorRows:
                            parallelcoordinatesGeneratorRows[elementForXAxis].append(valueObj)
                        else:
                            parallelcoordinatesGeneratorRows[elementForXAxis] =  yAxisArray
                            parallelcoordinatesGeneratorRows[elementForXAxis].append(valueObj)
                        xEntries.append(xAxis)
                
                
                      
                xEntries = self.unique(xEntries)   
                          
                strResult = "[ "
                strResult = "[ "
                for element in parallelcoordinatesGeneratorRows:
                    #print "parallelcoordinatesGeneratorRows##############################",parallelcoordinatesGeneratorRows 
                    values = parallelcoordinatesGeneratorRows[ element ]         
                    strValueObject = ""
                    
                    
                    #print "Values##################################################", values
                    strContent = ""
                    valueKeys = []
                    for value in values:
                        for key in value.keys():
                            #print "key##############################",key 
                            valueKeys.append(key)
                            if value[key]:
                                strContent = strContent + '"'+key+'"'+":" + value[key]+","
                            else:
                                strContent = strContent + '"'+key+'"'+":0.0,"
                     
                    strContent = strContent + '"'+key+'"'+":" + value[key]+"," + '"'+"Labels"+'"'+":" + '"'+element+'"'+","
                    #strContent = strContent + '"'+key+'"'+":" + value[key]+","  
                    #print "key##############################",key         
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
               
                
                lineArraytwo = []
                for i in range(len(lineArray)):
                    #print "##########################", lineArray[i]
                    lineObject = {'name': lineArray[i]}
                
                
                    lineArraytwo.append(lineObject)
                
                
                lineArraytwo = self.unique(lineArraytwo)
                code=code.replace("@@@DATA@@@", "".join(strResult)) 
                code=code.replace("@@@LINE@@@", simplejson.dumps(str(lineArraytwo)))
                   
                print "CODEEEEEEEEEEEEEEEEEEEEEEEEEE", strResult            
                '''self.results['code']=codeTwo
                print "CODEEEEEEEEEEEEEEEEEEEEEEEEEE", self.results'''  
                            
           
            
            if len(tableForDimArray) == 3:     
                
                xAxisUri = ""   
                code=self.codeObject['code']
                #print "lllllllllllllllllllllllllllll", code
                lineArray = []
                
                indexForLine2Axis = self.getDimensionIndex2("Line", indexForXAxis, indexForLineAxis )
                #print  "##########################################", indexForXAxis, "####################################", indexForLineAxis, "###############", indexForLine2Axis   
                for i in range(len(tableForDimArray)-2):
                    parallelcoordinatesGeneratorRows = {}
                    
                    
                    for element in self.mappingInfoValue:
                       
                        
                        
                        
                        xAxis = element['observation']['dimensionlabel%s'% (indexForXAxis)]  
                        xAxisUri = element['observation']['dimensionuri%s'% (indexForXAxis)] 
                        line = element['observation']['dimensionlabel%s'% (indexForLineAxis)] 
                        lineArray.append(line)
                       
                       
                        
                        line2 = element['observation']['dimensionlabel%s'% (indexForLine2Axis)]
                        yAxisArray = []               
                        elementForXAxis = line2
                        yAxis = element['observation']['measurevalue']
                        
                        
                        
                        
                         
                        
                        valueObject = {line : yAxis}                
                        valObj = {xAxis : valueObject}
                        if elementForXAxis in parallelcoordinatesGeneratorRows:
                            parallelcoordinatesGeneratorRows[elementForXAxis].append(valObj)
                        else:
                            parallelcoordinatesGeneratorRows[elementForXAxis] =  yAxisArray
                            parallelcoordinatesGeneratorRows[elementForXAxis].append(valObj)   
                         
           
                st = "http://data.lod2.eu/"   
                sparqlqueryObject = "" 
                if st in self.dataset:    
                    sparqlqueryObject = SPARQLQuery('http://open-data.europa.eu/en/sparqlep', 'regex')
            
                else:
                    sparqlqueryObject = SPARQLQuery('http://zaire.dimis.fim.uni-passau.de:8890/sparql', 'virtuoso')
                 
                 
                 
                 
                 
                nullIndexUri = ""
                if indexForXAxis == 1:
                    nullIndexUri  =  element['observation']['dimensionuri%s'% (indexForXAxis)] 
                    
                if indexForLineAxis == 1:
                    nullIndexUri  = element['observation']['dimensionuri%s'% (indexForLineAxis)] 
                    
                     
                if indexForLine2Axis == 1:
                    nullIndexUri  = element['observation']['dimensionuri%s'% (indexForLine2Axis)] 
                    
                 
                #print "GENOMMEN: :: :: ::: : ", nullIndexUri
                labelOfdim = sparqlqueryObject.get_label_of_dimensions(self.dataset,nullIndexUri )
                
                
                
                
                
                labOfdm = labelOfdim [0]['label']
                
                #print "LABEL OF DIM: ", labelOfdim
                
                
                lineBundle = [ ]
                for element in parallelcoordinatesGeneratorRows:
                    #print "ELEMENT#####################################    ", element
                    values = parallelcoordinatesGeneratorRows[ element ]                    
                    strValueObject = ""
                    
                    strContent = ""
                    valueKeys = []
                    for value in values:
                        for element2 in value:
                            vals = value[ element2 ]
                            for key in vals.keys():
                                commonElementMap = self.getCommonElementMap( lineBundle, key )
                                if commonElementMap:
                                    mapAttr = self.getCommonElementMap(commonElementMap, element )   
                                                                                                     
                                    if mapAttr:
                                        objMap = { 'attr' : element2, 'value': vals[key]}
                                        mapAttr.append(objMap)
                                    else:
                                        objMap =  { 'common': element, 'map': [ { 'attr' : element2, 'value': vals[key]} ]} 
                                        commonElementMap.append(objMap)                                 
                                else:
                                    
                                    obj = { 'common' : key, 'map' : [] }                                   
                                    mapAttr =  { 'common': element, 'map': [ { 'attr' : element2, 'value': vals[key]} ]} 
                                    
                                    obj['map'].append(mapAttr)                                    
                                    lineBundle.append(obj)
                                    
                
                self.sortLineBundle(lineBundle)
                attrArray = []       
                strResult = "[ "
                for item in lineBundle:
                    mapArray =  item ['map']
                   
                    #print "ELEMENT ----------------------", mapArray
                    for maps in mapArray:
                        mapArrayTwo =  maps ['map']
                        comm = maps ['common']
                        
                
                        
                        comArray = []
                        if comm.isdigit():
                            
                            comArray = [{labOfdm: comm}]
                            #print "GEMAPPT: KEY: ", comArray
                        else:
                            #print "false", comm 
                            comArray = [{'Labels': comm}]
                           
                           
                        generatorRows = {}
                        for attrs in mapArrayTwo: 
                            att =  attrs ['attr']
                            val = attrs ['value']
                            
                            attrObject = {att : val }
                            #print "HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", attrObject
                            if comm in generatorRows:
                                generatorRows[comm ].append(attrObject)
                                attrArray. append (generatorRows)
                            else:
                                generatorRows[comm] =  comArray 
                                generatorRows[comm].append(attrObject)
                                attrArray. append (generatorRows)
                            #print "HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE",  comArray 
                            
                    attrArrays = self.unique(attrArray)        
                    
                    strValueObject = ""
                    
                    strContent = ""
                    valueKeys = []
                    finalArray = []
                    for element in attrArrays:
                        #print "element##################################", element
                        for x in element:
                            #print "------------------------------------->", element[key]
                            elementArray = element[x]
                            #print "strcontenntttt ############", elementArray, "xxxxxxxxxxxxxxxxxxxxxxx", x
                            
                            #for entry in elementArray:
                            sContent = ""
                            for i in range(len(elementArray)):
                                #print "lLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLl", elementArray[i]
                                entry = elementArray[i]
                               
                                    
                                for key in entry.keys():
                                    sContent = sContent + '"'+key+'"'+":" + '"'+entry[key]+'"'+','
                                    #print "KEYYYYYYYYYYYYYYYYYYYYYYYYYYyy", key, "           ", entry[key]
                            
                            tempList2 = list(sContent)
                            tempList2[len(tempList2)-1]=""
                            sContent = "".join(tempList2)
                            sContent = "{ " + sContent + "}, "
                            #print ">>> SCONTENT: ", sContent
                                
                        strContent = strContent + sContent
                                
                #print "##########################################",  strContent               
                tempList = list(strContent)
                tempList[len(tempList)-1]=""
                strEndContent = "".join(tempList)
                
                #strValueObject = "{" +strEndContent+ "}, "             
                toDictObject = strEndContent               
                strResult = strResult + toDictObject
                
              
                tempList = list(strResult)
                tempList[len(tempList)-1]=""
                strEndResult = "".join(tempList)
                strResult = strEndResult + "]"
         
                lineArraytwo = []
                for i in range(len(lineArray)):
                    #print "##########################", lineArray[i]
                    lineObject = {'name': lineArray[i]}
                    
                    
                    lineArraytwo.append(lineObject)
                
                
                #print "RESULTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT", strResult
                lineArraytwo = self.unique(lineArraytwo)
                code = code.replace("@@@LINE@@@", simplejson.dumps((lineArraytwo)))
                
                code = code.replace("@@@DATA@@@", "".join(strResult))
            #print "CODE\n", code 
          
            ''' lineStr = ""
            for i in range(len(lineArray)):
                #print "LINESSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS", lineArray
                lineStr = lineStr + """
                
                    var colorText%s = "<font style=\'background-color: "+foreground.strokeStyle+"\'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT>"
                    var line%s = %s;
                    globalLegend.push( {"cluster":line%s, "color": colorText%s} ); 
                    
                
                """%(i, i,  '"' + lineArray[i] + '"', i, i)
             
               
            code=code.replace("@@@LINE@@@", lineStr)'''
            
            
            #self.results['code']=code
            
            self.results['code']=code
            indexForXAxis = None
            indexForLineAxis = None
            indexForLineAxis = None       
                #addRows=self.transformRows(parallelcoordinatesGeneratorRowsArray)
        except Exception as ex:
            raise Exception("-ParallelGenerator.transform: %s"%ex)
    
    def getCommonElementMap(self, commonArray, commonName):
        for element in commonArray:
            if element['common'] == commonName:
                return element['map'] 
    
        return None
   
    def sortLineBundle(self, lineBundle):
        
        for element1 in lineBundle:
            objmap1 =  element1['map']
            
            for element2 in objmap1:
                objmap2 = element2['map']
                #print "::::: VORHER ", objmap2
                element2['map'] = sorted(objmap2, key=itemgetter('attr'))
                #print "::::: NACHER ", element2['map']
            
            
    
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
            #print "###################################clientObj", self.mappingInfoDimension
            cubeComponent = clientObj['cubecomponent']
            if cubeComponent == channelName:
                mappedDimensionUri = clientObj['dimensionuri']
                #print "mappedDimensionUri##############################", mappedDimensionUri
                mappedDimensionLabel = clientObj['label']
                mappedDimensionIndex = clientObj['index']            
                return mappedDimensionIndex
                    
           
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
                