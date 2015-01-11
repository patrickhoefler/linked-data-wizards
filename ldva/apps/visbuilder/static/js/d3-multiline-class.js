/*
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
*/

var lineChart = function (datarows, channelMappings, targetSelector, chartRowIndex){
    console.log(chartRowIndex);
    // top, right, bottom, left - Margins
    var margin = [10, 200, 170, 100],
        width = 850 - margin[1] - margin[3],
        height = 600 - margin[0] - margin[2];

    var x = d3.scale.ordinal().rangePoints([0, width]);
    var y = d3.scale.linear().range([height, 0]);

    var xAxis = d3.svg.axis().scale(x).orient("bottom");
    var yAxis = d3.svg.axis().scale(y).orient("left");

    var svg = d3.select(targetSelector).append("svg:svg")
        //.attr("width", width + margin[1] + margin[3])
        //.attr("height", height + margin[0] + margin[2])
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", "0 0 " + (width + margin[1] + margin[3]) + " "+ (height + margin[0] + margin[2]))
        .attr("class", "multiline")
        .append("svg:g")
        .attr("transform", "translate(" + margin[3] + "," + margin[0] + ")");
    var labels = d3.scale.category20();

    var line = d3.svg.line()
        .x(function(d) { /*console.log('line x, y:' + d.year + '; x(year):' + x(d.year) + '; y(measure):' + y(d.measure));*/ return x(d.xAxis); })
        .y(function(d) { return y(d.yAxis); });
		
    function getValuesPerLabel(label, data){
        var returnValues = [];
        for(var i=0; i<data.length; i++){
            if (data[i].label == label){
                returnValues.push({xAxis: data[i].xAxis, yAxis: +data[i].yAxis});
            }
        }
		returnValues = returnValues.sort(function(a,b){ if (a.xAxis < b.xAxis) return -1; if (a.xAxis > b.xAxis) return 1; return 0; });
        return returnValues;
    }

    function getClassName(label){
        var replacer = new RegExp(" ","g");
        var className = label.replace(replacer, "-").toLowerCase();
        return className;
    }

    brushingObserver.registerListener(function(newChartRowIndex){
        chartRowIndex = newChartRowIndex;
        targetSelector = '#vis-row' + chartRowIndex + ' .vis'; // workaround
    }, chartRowIndex, brushingDataUpdated, brushingDataUpdatedByDimension);

    function brushingDataUpdated(selectedData){
        //return;

        if (selectedData == null)
            return resetSelection();

        var lineLabels = svg.selectAll(".lineLabel");
        lineLabels.each(function(lineLabel) {
            if (lineLabel) {
                var rawDates = getRawDatesFromLineLabel(lineLabel);
                lineLabel.selected = false;
                for(var j=0; j<rawDates.length; j++){
                    for(var i=0; i<selectedData.length; i++){
                        if (selectedData[i].compare(rawDates[j]))
                            lineLabel.selected = true;
                    }
                }
            }
        });
        lineLabels.classed("notselected", function(d) { return !d.selected; });
    }

    function resetSelection(){
        svg.selectAll(".lineLabel").classed("notselected", function(d) { return false; });
    }

    function brushingDataUpdatedByDimension(selectedDimensions){
        //console.log('callback data changed... Multiline');

        if (selectedDimensions == null)
            return resetSelection();

        var yChannel = charting.getChannelMappingForChannel(channelMappings, "y-Axis");
        var ySelectedDimension = charting.getDimensionByUri(selectedDimensions, yChannel.uri);
        if (ySelectedDimension != null)
            return setLinesSelectedWhereYValueSelected(ySelectedDimension);

        var linesChannel = charting.getChannelMappingForChannel(channelMappings, "Lines");
        var linesSelectedDimension = charting.getDimensionByUri(selectedDimensions, linesChannel.uri);
        if (linesSelectedDimension != null)
            return setLinesSelectedWhereLineSelected(linesSelectedDimension);

        return resetSelection();
    }

    function setLinesSelectedWhereYValueSelected(selectedDimensionY) {
        var lineLabels = svg.selectAll(".lineLabel");
        lineLabels.each(function (lineLabel) {
            if (lineLabel) {
                //var rawDates = getRawDatesFromLineLabel(lineLabel);
                lineLabel.selected = false;
                for (var j = 0; j < lineLabel.values.length; j++) {
                    if (selectedDimensionY.from != null && lineLabel.values[j].yAxis >= selectedDimensionY.from && lineLabel.values[j].yAxis <= selectedDimensionY.to) {
                        lineLabel.selected = true;
                        return;
                    } else if (selectedDimensionY.values != null && _.contains(selectedDimensionY.values, lineLabel.values[j].yAxis)) {
                        lineLabel.selected = true;
                        return;
                    }
                }
            }
        });
        lineLabels.classed("notselected", function(d) { return !d.selected; });
    }

    function setLinesSelectedWhereLineSelected(selectedDimension) {
        var lineLabels = svg.selectAll(".lineLabel");
        lineLabels.each(function (lineLabel) {
            if (lineLabel) {
                //var rawDates = getRawDatesFromLineLabel(lineLabel);
                lineLabel.selected = false;
                for (var j = 0; j < lineLabel.values.length; j++) {
                    if (selectedDimension.from != null && lineLabel.label >= selectedDimension.from && lineLabel.label <= selectedDimension.to) {
                        lineLabel.selected = true;
                        return;
                    } else if (selectedDimension.values != null && _.contains(selectedDimension.values, lineLabel.label)) {
                        lineLabel.selected = true;
                        return;
                    }
                }
            }
        });
        lineLabels.classed("notselected", function(d) { return !d.selected; });
    }

    function getRawDatesFromLineLabel(lineLabel){
        var returnDataRows = [];
        for (var i=0; i<lineLabel.values.length; i++){
            var returnDataRow = [];
            var cValue = lineLabel.values[i];
            for(var j=0; j<channelMappings.length; j++){
                if (channelMappings[j].channel == 'x-Axis'){
                    returnDataRow[j] = cValue.xAxis;
                } else if (channelMappings[j].channel == 'y-Axis'){
                    returnDataRow[j] = cValue.yAxis;
                } else if (channelMappings[j].channel == 'Lines'){
                    returnDataRow[j] = lineLabel.label;
                }
            }
            returnDataRows.push(returnDataRow);
        }
        return returnDataRows;
    }

    function getSelectedDimensionsFromLabel(line){
        var linesDimension = charting.getChannelMappingForChannel(channelMappings, "Lines");
        var dimensionLine = {
            from: line.label,
            to: line.label,
            uri: linesDimension.uri,
            label: linesDimension.label,
            type: linesDimension.type
        };
        return [dimensionLine];
    }

    var drawVisualization = function(datarows) {

        var data = [];
        for(var i=0; i<datarows.length; i++){
            var d = datarows[i];
	
            var newObj = { bubbleSize:Math.random() };
            for(var j=0; j<channelMappings.length; j++){
                if (channelMappings[j].channel == 'x-Axis'){
                    newObj.xAxis = d[j];
                } else if (channelMappings[j].channel == 'y-Axis'){
                    newObj.yAxis = +d[j];
                } else if (channelMappings[j].channel == 'Lines'){
                    newObj.label = d[j];
                }
            }
            data.push(newObj);
        }

        var xLabel, yLabel;
		var dataTypes = { bubbleSize : null };
        for(i=0; i<channelMappings.length; i++){
            if (channelMappings[i].channel == 'x-Axis'){
                xLabel = channelMappings[i].label;
				dataTypes.xAxis = channelMappings[i].datatype;
            } else if (channelMappings[i].channel == 'y-Axis'){
                yLabel = channelMappings[i].label;
				dataTypes.yAxis = channelMappings[i].datatype;
            }else if (channelMappings[i].channel == 'Lines'){
				dataTypes.Lines = channelMappings[i].datatype;
			}
        }

        // sort data by color, to get a overall-equal mapping of the legend.
        data = _.sortBy(data, function(dataObject){return dataObject.label});
        labels.domain(_.map(data, function(dataObject){ return dataObject.label; }));

        var lineObjects = labels.domain().map(function(label) {
            return {
                label: label,
                values: getValuesPerLabel(label, data)
            };
        });

		lineObjects = lineObjects.sort(function(a,b){ if (a.label < b.label) return -1; if (a.label> b.label) return 1; return 0; });
        x.domain(data.map(function(d) { return d.xAxis; }).sort(function(a,b){ if (a < b) return -1; if (a > b) return 1; return 0; }));
        y.domain([
            d3.min(lineObjects, function(c) { return d3.min(c.values, function(v) { return v.yAxis; }); }),
            d3.max(lineObjects, function(c) { return d3.max(c.values, function(v) { return v.yAxis; }); })
        ]);
		if (dataTypes.xAxis != 'string'){
			var xCount = d3.max(data, function(d) { return d.xAxis; }) - d3.min(data, function(d) { return d.xAxis; });
			xAxis.ticks(xCount);
		}

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis)
            .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "-.8em")
                .attr("dy", ".15em")
                .attr("transform", function() { return "rotate(-65)" });

        svg.select("g.x.axis")
            .append("text")
            .attr("class", "label")
            .attr("x", width)
            .attr("y", -6)
            .style("text-anchor", "end")
            .text(xLabel)
            .on('click', function(){
                Vis.view.getNewAxisLabel(xLabel, function(newAxisLabel){ svg.select("g.x.axis text.label").text(newAxisLabel); });
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
            .text(yLabel)
            .on('click', function(){
                Vis.view.getNewAxisLabel(yLabel, function(newAxisLabel){ svg.select("g.y.axis text.label").text(newAxisLabel); });
            });

        var labelDomElements = svg.selectAll(".lineLabel")
            .data(lineObjects)
            .enter().append("g")
            .attr("class", function(d){return "lineLabel label-" + getClassName(d.label)});

        labelDomElements.append("path")
            .attr("class", "linechart")
            .attr("d", function(d) { return line(d.values); })
            .style("stroke", function(d) { return labels(d.label); })
            .style("stroke-width", "2");

        labelDomElements.append("path")
            .attr("class", "linechart-background")
            .attr("d", function(d) { return line(d.values); })
            .style("stroke", "transparent")
            .on("mouseover", function (d) {
                //console.log('over: ' + d.label);
                d3.select(this).style("stroke", "black");
                d3.select(".label-" + getClassName(d.label) + " text")
                    .style("fill", "black");
                d3.select(".label-" + getClassName(d.label) + " .linechart")
                    .style("display", "none");
                brushingObserver.update(chartRowIndex, getRawDatesFromLineLabel(d), getSelectedDimensionsFromLabel(d));
            })
            .on("mouseout", function (d) {
                var labelClassName = getClassName(d.label);
                d3.select(this).style("stroke", "transparent");
                d3.select(".label-" + labelClassName + " text")
                    .style("fill", "transparent");
                d3.select(".label-" + labelClassName + " .linechart")
                    .style("display", "block");
                brushingObserver.update(chartRowIndex, null, null);
                brushingDataUpdated(null);
            });

        labelDomElements.append("text")
            .datum(function(d) { return {label: d.label, value: d.values[d.values.length - 1]}; })
            .attr("transform", function(d) { return "translate(" + x(d.value.xAxis) + "," + y(d.value.yAxis) + ")"; })
            .attr("x", 3)
            .attr("dy", ".35em")
            .style("fill", "transparent")
            .text(function(d) { return d.label; });

        var legend = svg.selectAll(".lineLabel2")
            .data(lineObjects)
            .enter().append("g")
            .attr("class", function(d){return "lineLabel2 label-" + getClassName(d.label)});

        var counter=0;
        legend.append("text")
         .attr("transform", function(d) { counter++; return "translate(" + (width+120) + "," + counter*14 + ")"; })
         .style("fill", function(d) { return labels(d.label); })
         .text(function(d) { return d.label; })
            .on("mouseover", function (d) {
                var labelClassName = getClassName(d.label);
                d3.select(".label-" + labelClassName + " .linechart-background").style("stroke", "black");
                d3.select(".label-" + labelClassName + " text").style("fill", "black");
                d3.select(".label-" + labelClassName + " .linechart").style("display", "none");
                brushingObserver.update(chartRowIndex, getRawDatesFromLineLabel(d), getSelectedDimensionsFromLabel(d));
            })
            .on("mouseout", function (d) {
                var labelClassName = getClassName(d.label);
                d3.select(".label-" + labelClassName + " .linechart-background").style("stroke", "transparent");
                d3.select(".label-" + labelClassName + " text").style("fill", "transparent");
                d3.select(".label-" + labelClassName + " .linechart").style("display", "block");
                brushingObserver.update(chartRowIndex, null, null);
            });
    };

    drawVisualization(datarows);
};