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
class ParallelGeneratorOne(generator.Generator):
    
    #print "Halloooooooooooooooooooooooooooooooo"
    mappingInfoDimension = None
    mappingInfoMeasure = None
    dimensions = None
    
    codeObjectTwo= {'code': """var loc=config.location;function drawParallelCoordinates() {
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
    w = 960 - m[1] - m[3],
    h = 340 - m[0] - m[2];

var x = d3.scale.ordinal().rangePoints([0, w], 1),
    y = {};

var line = d3.svg.line(),
    axis = d3.svg.axis().orient("left"),
    foreground,
    dimensions,
    brush_count = 0;
var data = @@@DATA@@@;
var colors = d3.scale.category20();
//var colors = color(Math.random());
console.log(colors);

d3.selectAll("canvas")
    .attr("width", w + m[1] + m[3])
    .attr("height", h + m[0] + m[2])
    .style("padding", m.join("px ") + "px");

foreground = document.getElementById('foreground').getContext('2d');

foreground.strokeStyle = "rgba(0,100,160,0.1)";

var svg = d3.select("#"+loc).append("svg:svg")
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

  // Create a scale for each.
 dimensions.forEach(function(d) {
    var vals = data.map(function(p) {return p[d];}); 
    if (vals.every(quant_p) && d !== "Year"){ 
      y[d] = d3.scale.linear()
          .domain(d3.extent(vals.map(function(p){return +p})))
          .range([h, 0]);}
    else{
    
      y[d] = d3.scale.ordinal()
          .domain(vals.filter(function(v, i) {return vals.indexOf(v) == i;}))
          .rangePoints([h, 0],1);}
  })
  
  /*dimensions.forEach(function(d) {
    var vals = data.map(function(p) {return p[d];}); 
    if ( vals >=2003 && vals <=2008){
    console.log(vals);
        y[d] = d3.scale.ordinal()
          .domain(vals.filter(function(v, i) {return vals.indexOf(v) == i;}))
          .rangePoints([h, 0],1);}

    else if (vals.every(quant_p)){ 
      y[d] = d3.scale.linear()
          .domain(d3.extent(vals.map(function(p){return +p})))
          .range([h, 0]);}
    else{
    
      y[d] = d3.scale.ordinal()
          .domain(vals.filter(function(v, i) {return vals.indexOf(v) == i;}))
          .rangePoints([h, 0],1);}
  })*/
  
  
  
  
  // Render full foreground
  paths(data, foreground, brush_count);

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
      .attr("x", -12)
      .attr("width", 24);

  // Handles a brush event, toggling the display of foreground lines.
  function brush() {
    brush_count++;
    var actives = dimensions.filter(function(p) { return !y[p].brush.empty(); }),
        extents = actives.map(function(p) { return y[p].brush.extent(); });

    // Get lines within extents
    var selected = [];
    data.map(function(d) {
      return actives.every(function(p, i) {
        var p_new = (y[p].ticks)?d[p]:y[p](d[p]); //convert to pixel range if ordinal
          return extents[i][0] <= p_new && p_new <= extents[i][1];
      }) ? selected.push(d) : null;
    });

    // Render selected lines
    foreground.clearRect(0,0,w+1,h+1);
    paths(selected, foreground, brush_count);
  }

  function paths(data, ctx, count) {
    var n = data.length,
        i = 0,
        reset = false;
    function render() {
      var max = d3.min([i+60, n]);
      data.slice(i,max).forEach(function(d) {
      //console.log(colors(d));
        path(d, foreground, colors(d));
        
      });
      i = max;
    };
    (function animloop(){
      if (i >= n || count < brush_count) return;
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

   
    def __init__(self, mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue, dataset):
        self.mappingInfoDimension = mappingInfoForDimension
        
        #print "------------------------------------------------", self.mappingInfoDimension
        self.mappingInfoMeasure = mappingIngfoForMeasure
        
        self.mappingInfoValue = mappingInfoForValue
        self.dataset = dataset
        self.results = {'code':'', 'errors': [], 'mappinginfo': {}}
        print "------------------------------------------------", self.mappingInfoValue        
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
                dimLabel = entry['label']
                tableForDim = {'dimension' : '', 'label': ''}
                
                tableForDim['dimension'] = dim
                tableForDim['label'] = dimLabel
                tableForDimArray.append(tableForDim)
                
                
                
            tableForMesArray = []
            for meas in self.mappingInfoMeasure:
                value = meas ['measureuri']
                label = meas ['label']
                tableForMeasure = {'measure' : '', 'label': ''}
                tableForMeasure ['measure'] = value
                tableForMeasure ['label'] = label
                
                tableForMesArray.append (tableForMeasure)   
             
             
             
            
            strResult = "[ "   
            xAxisArray = []
            for element in self.mappingInfoValue:
               
                    strg = "" 
                    strg2 = ""
                    for i in range(len(tableForDimArray)):                 
                        xAxis = element['observation']['dimensionlabel%s'% (i)]
                        labelForValue = tableForMesArray[0]['label']
                        label2 = tableForDimArray[i]['label']
                        
                        strg = strg + '"'+label2+'":"'+xAxis+'",'
                        
                    yAxis = element['observation']['measurevalue']    
                    #print "iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii", yAxis
                    strg2 = strg+'"'+labelForValue + '":"'+ yAxis+'"'
                    
                    '''tempList1 = list(strg2)
                    tempList1[len(tempList1)-1]=""
                    strEndContent1 = "".join(tempList1)''' 
                    
                    strValueObject = "{" +strg2+ "}, "             
                    toDictObject = strValueObject               
                    strResult = strResult + toDictObject
                    
            tempList = list(strResult)
            tempList[len(tempList)-2]=""
            strEndResult = "".join(tempList)
                    
            strResult = strEndResult + "]"
    
        
                
            print "DIMMMMMURIIIII",  strResult
        
             
            code=code.replace("@@@DATA@@@", "".join(strResult)) 
           
               
            #print "CODEEEEEEEEEEEEEEEEEEEEEEEEEE", strResult            
            self.results['code']=code
            #print "CODEEEEEEEEEEEEEEEEEEEEEEEEEE", self.results 
                                      
                            
                            
                                  
            #print "ooooooooooooooooooooooooooooooooooooooooo", parallelcoordinatesGeneratorRows      
        except Exception as ex:
            raise Exception("-ParallelGeneratorOne.transform: %s"%ex)
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
                