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

class PieChartGenerator(generator.Generator):
    mappingInfoDimension=None
    mappingInfoMeasure=None
    dimensions=None

    labelOfDimensionArray=[]
    labelOfMeasureArray=[]
    measureContentArray=[]
    codeObject={'code': """

var loc = config.location;
var w = 800,
    h = 500,
    r = 200,
    color = d3.scale.category20();


var data = @@@DATA@@@;
var chartRoxIndex = @@@CHARTROWINDEX@@@;
var uriOfPieDimension = '@@@URIOFPIEDIMENSION@@@';

var vis = d3.select("body")
        .select("#" + loc)
        .append("svg:svg")
        .attr('class', 'pie')
        .data([data])
        //.attr("width", w)
        //.attr("height", h)
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", "0 0 " + w + " " + h)
        .append("svg:g")
        .attr("transform", "translate(" + r + "," + r + ")");


var arc = d3.svg.arc()
        .outerRadius(r);


var pie = d3.layout.pie()

.value(function(d) { return d.value; });


 var colorArray =  [];
var arcs = vis.selectAll("g.slice")
        .data(pie)
        .enter()
        .append("svg:g")
        .attr("class", "slice");

 var strgPie = [];
 var strgPie2 = [];

arcs.append("svg:path")
        .attr("fill", function(d, i) { return color(i); } )
        .attr("d", arc)

        . on("click", function (d, i) {

            var  strgPie2 = [];

             d3.select(this).style("stroke", "black")
            //.style("fill", "black");
            .style("fill", "blue")
                .append("title")
                .text(function(d, i) {


                     return d.value;
                })



            var cachedpie = d.data;
            var lab = cachedpie.label;
            var val = cachedpie.value;

            if (strgPie.length > 0){
               for (var j = 0; j<strgPie.length; j++){
                    if (strgPie[j][0] ==  lab /*&& strgPie[j][1] ==  parseFloat( val)*/ ) {
                     d3.select(this).style("stroke", "transparent")
                .style("fill", function(d) {  return color(i); })

                        //alert("ein fund len: " +strgPie.length);
                        console.log(strgPie);

                        strgPie.splice(j, 1);

                        updater (strgPie);
                        return;

                    }
                }

          }


            strgPie.push([ lab,parseFloat( val)]);

            updater (strgPie);




            /*strgPie.push([ lab,parseFloat( val)]);
            updater (strgPie);*/


        })




        ;











arcs.append("svg:text")
    .attr("transform", function(d) {


d.innerRadius = 0;

d.outerRadius = r;

return "translate(" + arc.centroid(d) + ")";
})

.attr("text-anchor", "middle")
.text(function(d, i) { /*console.log ("hierr"); console.log( data);*/  return data[i].label; });

function updater (selectData){

    brushingObserver.update(chartRoxIndex, selectData);

}

brushingObserver.registerListener(function(newChartRowIndex){ chartRowIndex = newChartRowIndex; }, chartRoxIndex, function (selectedData) {

    if ( selectedData == null ){
        resetSelection();
    } else{
        getNotSelectedData(selectedData);
    }
    strgPie = [];

},function (selectedDimensions) {
    if (selectedDimensions == null){
        resetSelection();
    } else {
        var selectedDimensionPie = charting.getDimensionByUri(selectedDimensions, uriOfPieDimension);
        if (selectedDimensionPie != null) {
            getNotSelectedDimensions(selectedDimensionPie);
        } else {
            resetSelection();
        }
    }
    strgPie = [];
});

function resetSelection(){
    $('.slice').each(function (index, slice) {
        var color = ($(slice).find('path').attr('fill'));
        $(slice).find('path').first().css('fill', color)
    });
}


function getNotSelectedData (selectedData){




   $('.slice').each(function (index, slice) {
   var color = ($(slice).find('path').attr('fill'))
        $(slice).find('path').first().css('fill', color)

        var currentSliceSelected = false;

        selectedData.forEach(function (selectedEntity) {

            if ($(slice).find('text').first().text() === selectedEntity[0]) {
                currentSliceSelected = true;
            }

        });

        if (!currentSliceSelected) {
            $(slice).find('path').first().css('fill', '#666')
        }



    });


    /*for (var i = 0; i < selectedData.length; i++ ) {
        var firstArray = selectedData[i];
        var label = firstArray[0];

        for (var j = 0; j< arr.length; j++) {
            if (arr[j][0] == label) {
                var color = arr[j][1];

                for (var cnt = 0; cnt < pathList.length; cnt++) {
                    var piepath = $('.pie path[fill="' + color + '"]');
                    console.log(piepath);


                }
            }
        }
    }*/

}

function getNotSelectedDimensions (selectedDimension){
    $('.slice').each(function (index, slice) {
        var color = ($(slice).find('path').attr('fill'));
        $(slice).find('path').first().css('fill', color);
        var currentSliceSelected = false;
        if (selectedDimension.values != null){
            selectedDimension.values.forEach(function (selectedDimensionValue) {
                if ($(slice).find('text').first().text() === selectedDimensionValue) {
                    currentSliceSelected = true;
                }
            });
        }
        if (!currentSliceSelected) {
            $(slice).find('path').first().css('fill', '#666')
        }
    });
}


function getColor(){


$('.slice').each(function (index, slice) {

   var color = ($(slice).find('path').attr('fill'))
        $(slice).find('path').first().css('fill', color)





    });


}

"""}
    results={'code':'', 'errors':[]}

    def __init__(self, mappingInfoForDimension, mappingIngfoForMeasure, mappingInfoForValue, dataset, chartrowIndex):
        self.mappingInfoDimension=mappingInfoForDimension
        self.mappingInfoMeasure=mappingIngfoForMeasure

        self.mappingInfoValue=mappingInfoForValue
        self.chartRoxIndex = chartrowIndex
        self.results={'code':'', 'errors': []}

    def transform(self):
        try:
            code=""
            d3PieChartGeneratorRowsArray=[]
            tableForDim = {'dimension' : ''}
            for entry in self.mappingInfoDimension:
                dim = entry['dimensionuri']
                dimlable = entry['label']
                tableForDim['dimension'] = dim
            #sprint "LENGTHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH", len(tableForDim)

            for i in range(len(tableForDim)):
                for element in self.mappingInfoValue:
                    xAxis = element['observation']['dimensionlabel%s'% (i)]
                    yAxis = element['observation']['measurevalue%s'%(i)]

                    d3PieChartGeneratorRows=[xAxis, yAxis]
                    d3PieChartGeneratorRowsArray.append(d3PieChartGeneratorRows)
                    d3PieChartGeneratorRowsArray=self.unique(d3PieChartGeneratorRowsArray)


            addRows=self.transformRows(d3PieChartGeneratorRowsArray)
            code=self.codeObject['code']

            code=code.replace("@@@DATA@@@", addRows)
            code = code.replace("@@@CHARTROWINDEX@@@", self.chartRoxIndex)
            code = code.replace("@@@URIOFPIEDIMENSION@@@", tableForDim['dimension'])

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
            raise Exception("-d3PieChartGenerator.transformRows: %s"%ex)


