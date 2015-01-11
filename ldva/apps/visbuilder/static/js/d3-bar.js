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

var barChart = function (datarows, channelMappings, targetSelector, chartRowIndex, showChartRotated){

    // top, right, bottom, left
    //var margin = [20, 200, 170, 90],
    //    width = 750 - margin[1] - margin[3],
    //    height = 600 - margin[0] - margin[2];

    var margin = {top: 20, right: 20, bottom: 170, left: 40},
        width = 750 - margin.left - margin.right,
        height = 600 - margin.top - margin.bottom;

    var bars;
    var yAxisOrient = "left";
    var rotateTransformation = "";
    if (showChartRotated){
        var heightTemp = height;
        height = width;
        width = heightTemp;
        var marginCopy = margin;
        margin.left = marginCopy.top;
        margin.top = marginCopy.right;
        margin.right = marginCopy.bottom;
        margin.bottom = marginCopy.left;
        yAxisOrient = "right";
        var rotationCenterX = (width + margin.left + margin.right) / 2;
        var rotationCenterY = (height + margin.top + margin.bottom) / 2;
        rotateTransformation = " rotate(90 " + rotationCenterX + " " + rotationCenterY + ")";
    }

    var xLabel, yLabel;
    var dataTypes = { };
    for(var i= 0, max = channelMappings.length; i<max; i++){
        if (channelMappings[i].channel == 'x-Axis'){
            xLabel = channelMappings[i].label;
            dataTypes.xAxis = channelMappings[i].datatype;
        } else if (channelMappings[i].channel == 'y-Axis'){
            yLabel = channelMappings[i].label;
            dataTypes.yAxis = channelMappings[i].datatype;
        }
    }

    var x = d3.scale.ordinal()
        .rangeRoundBands([0, width], .1);

    var y = d3.scale.linear()
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient(yAxisOrient); // default: left

    var brush = d3.svg.brush()
            .x(x)
        .on('brushstart', brushstart)
        .on('brush', brushing)
        .on('brushend', brushend);

    var svg = d3.select(targetSelector).append("svg:svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", "0 0 " + (width + margin.left + margin.right) + " "+ (height + margin.top  + margin.bottom))
        .attr("class", "barchart")
        .append("svg:g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")" + rotateTransformation);

    function getValue(value, datatype){
        if (datatype == "string")
            return value;
        return +value;
    }

    function brushstart() {
        svg.classed("selecting", true);
    }

    function brushing() {
        var extent = d3.event.target.extent();
        bars.classed("selected", function(d) {
            return (extent[0] <= x(d.xAxis) && x(d.xAxis) + x.rangeBand() <= extent[1]);
        });
        updateBrushingListeners();
    }

    function brushend() {
        var selectionIsEmpty = d3.event.target.empty();
        svg.classed("selecting", !selectionIsEmpty);
        if (selectionIsEmpty){
            brushingObserver.updateEmpty(chartRowIndex);
            return
        }
        updateBrushingListeners();
    }


    function updateBrushingListeners(){
        var barsSelected = [];
        var selectedRawData = [];
        svg.selectAll(".selected").each(function(bar) {
            barsSelected.push(bar);
        });
        selectedRawData = _.map(barsSelected, function(bar) { return charting.getRawDataFromVisObject(bar, channelMappings); });
        var selectedDimensions = getBrushDimensions(barsSelected, brush.extent());
        brushingObserver.update(chartRowIndex, selectedRawData, selectedDimensions);
    }

    function getBrushDimensions(selectedRawBars, extend){
        var selectedDimensions = [];

        if (selectedRawBars == null || selectedRawBars.length == 0)
            return selectedDimensions;

        var xMapping = charting.getChannelMappingForChannel(channelMappings, 'x-Axis');
        var dimensionX = {
            from: d3.min(selectedRawBars, function(d){return d.xAxis;}),
            to: d3.max(selectedRawBars, function(d){return d.xAxis;}),
            uri: xMapping.uri,
            label: xMapping.label,
            type: xMapping.type
        };
        if (dataTypes.xAxis != "string"){
            dimensionX.from = extend[0][0];
            dimensionX.to = extend[1][0];
        }
        selectedDimensions.push(dimensionX);

        return selectedDimensions;
    }

    brushingObserver.registerListener(function(newChartRowIndex){
        chartRowIndex = newChartRowIndex;
        targetSelector = '#vis-row' + chartRowIndex + ' .vis'; // workaround
    }, chartRowIndex, function(selectedData){
        brush.clear();
        svg.selectAll('.brush').call(brush);
        svg.classed("selecting", (selectedData != null));
        if (selectedData == null){
            bars.classed("selected", false);
            return;
        }
        charting.setSelectedProperty(bars, selectedData, channelMappings);
        bars.classed("selected", function(b) { return b.selected; });

    }, function(selectedDimensions){
        brush.clear();
        svg.selectAll('.brush').call(brush);
        svg.classed("selecting", (selectedDimensions != null));

        if (selectedDimensions == null){
            if (bars) bars.classed("selected", true);
        } else {
            var channelMappingX = charting.getChannelMappingForChannel(channelMappings, 'x-Axis');
            var selectedDimensionX = charting.getDimensionByUri(selectedDimensions, channelMappingX.uri);
            if (selectedDimensionX != null){
                if (selectedDimensionX.from != null && selectedDimensionX.to != null){
                    var brushXFrom = x(selectedDimensionX.from);
                    var brushXTo = x(selectedDimensionX.to);
                    var extent = [brushXFrom - x.rangeBand()/2, brushXTo + x.rangeBand()/2];
                    setSelectedFromExtend(extent, false);
                } else if (selectedDimensionX.values != null) {
                    bars.each(function(visObject) {
                        if (visObject) {
                            visObject.selected = false;
                            for(var i= 0, max=selectedDimensionX.values.length; i<max; i++){
                                if (selectedDimensionX.values[i] == visObject.xAxis)
                                    visObject.selected = true;
                            }
                        }
                    });
                    bars.classed("selected", function(b) { return b.selected; });
                }
            }
        }
    });

    function setSelectedFromExtend(extent, doUpdateBrushingListeners) {
        if (extent[0] != extent[1]){ // if selectionArea is not empty
            bars.each(function(bar) {
                if (bar) {
                    //bar.selected = originalExtend[0] <= x(bar.xAxis)  && originalExtend[1] >= x(bar.xAxis);
                    bar.selected = extent[0] <= x(bar.xAxis) && x(bar.xAxis) <= extent[1];
                }
            });
            bars.classed("selected", function(d) { return d.selected; });
            if (doUpdateBrushingListeners)
                updateBrushingListeners();
        }
    }

    var drawVisualization = function(datarows) {

        // Map raw Data to Chart-Structure
        var data = [];
        var channelMappingLength = channelMappings.length;
        for(var i= 0, max = datarows.length; i<max; i++){
            var d = datarows[i];
            var newObj = { };
            for(var j= 0; j<channelMappingLength; j++){
                if (channelMappings[j].channel == 'x-Axis'){
                    newObj.xAxis = getValue(d[j], channelMappings[j].datatype);
                } else if (channelMappings[j].channel == 'y-Axis'){
                    newObj.yAxis = getValue(d[j], channelMappings[j].datatype);
                }
            }
            data.push(newObj);
        }

        data = _.sortBy(data, function(dataObject){return dataObject.xAxis});

        x.domain(data.map(function(d) { return d.xAxis; }));
        y.domain([0, d3.max(data, function(d) { return d.yAxis; })]);

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis)
            .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "-.8em")
                .attr("dy", ".15em")
                .attr("transform", function() { return "rotate(-65)" });

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .attr("transform", showChartRotated ? "translate(" + width + ", 0)" : "" )
        .append("text")
            .attr("class", "label")
            .attr("transform", "rotate(-90)")
            .attr("y", showChartRotated ? -15 : 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text(yLabel)
            .on('click', function(){
                Vis.view.getNewAxisLabel(yLabel, function(newAxisLabel){ svg.select("g.y.axis text.label").text(newAxisLabel); });
            });

        bars = svg.selectAll(".bar")
            .data(data);
        bars.enter().append("rect")
            .attr("class", "bar")
            .attr("x", function(d) { return x(d.xAxis); })
            .attr("width", x.rangeBand())
            .attr("y", function(d) { return y(d.yAxis); })
            .attr("height", function(d) { return height - y(d.yAxis); })
        .append("title")
            .text(function(d) { return d.yAxis });

        svg.append("g")
            //.attr("class", "brush")
            .classed('brush', true)
            .call(brush)
            .selectAll("rect")
            .attr("y", -6)
            .attr("height", height + 7);


        $(".bar").tipsy({ gravity: 's' });

    };

    drawVisualization(datarows);
};