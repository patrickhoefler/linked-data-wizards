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

//var globalY, globalX;
var bubbleChart = function (datarows, channelMappings, targetSelector, chartRowIndex){

    //function debug(){
    //    console.log('-------------------------------------------');
//
    //    var minX, minY, maxX, maxY;
    //    for(var j= 0, max = channelMappings.length; j<max; j++){
    //        var useOrdinalMapping = false;
    //        if (channelMappings[j].datatype == "string")
    //            useOrdinalMapping = true;
//
    //        if (channelMappings[j].channel == 'x-Axis'){
    //            var source = useOrdinalMapping ? x.rangeExtent() : x.domain();
    //            minX = source[0];
    //            maxX = source[1];
    //        }
    //        if (channelMappings[j].channel == 'y-Axis'){
    //            var source = useOrdinalMapping ? y.rangeExtent() : y.domain();
    //            minY = source[0];
    //            maxY = source[1];
    //        }
    //    }
    //    console.log('minX: ' + minX);
    //    console.log('minY: ' + minY);
    //    console.log('maxX: ' + maxX);
    //    console.log('maxY: ' + maxY);
//
    //    //console.log('x.rangeExtent(): ' + x.rangeExtent());
    //    console.log('x.domain(): ' + x.domain());
    //    console.log('y.domain(): ' + y.domain());
    //    console.log('x(x.domain()[1]): ' + x(x.domain()[1]));
    //    console.log('y(y.domain()[1]): ' + y(y.domain()[1]));
//
//
    //    console.log('y.getMinMaxPixel(): ' + y.getMinMaxPixel());
    //    console.log('x.getMinMaxPixel(): ' + x.getMinMaxPixel());
//
    //    console.log('-------------------------------------------');
    //    globalX = x;
    //    globalY = y;
    //}
//
    //function debugBrushed(extend){
    //    console.log('brushed: ');
    //    console.log(extend);
    //}


    // top, right, bottom, left
    var margin = [20, 200, 170, 90],
        width = 750 - margin[1] - margin[3],
        height = 600 - margin[0] - margin[2];

    var xLabel, yLabel;
    var dataTypes = { bubbleSize : null };
    for(var i= 0, max = channelMappings.length; i<max; i++){
        if (channelMappings[i].channel == 'x-Axis'){
            xLabel = channelMappings[i].label;
            dataTypes.xAxis = channelMappings[i].datatype;
        } else if (channelMappings[i].channel == 'y-Axis'){
            yLabel = channelMappings[i].label;
            dataTypes.yAxis = channelMappings[i].datatype;
        } else if (channelMappings[i].channel == 'Color'){
            dataTypes.bubbleColor = channelMappings[i].datatype;
        } else if (channelMappings[i].channel == 'Size'){
            dataTypes.bubbleSize = channelMappings[i].datatype;
        }
    }

    var x, y, size, color, dots, xAxis, yAxis, brush, svg;

    function getBrushForDomainForOrdinal(dom){
        return this(dom);
    }
    function getBrushForDomainForLinear(dom){
        return dom;
    }
    function getMinMaxPixelForOrdinal(){
        var range = this.rangeExtent();
        if (this.isY) // as linear returns 0/0 for the upper left corner, try to handle ordinal's extent in the same way...
            return [range[1], range[0]];
        return [range[0], range[1]];
        //return range;
    }
    function getMinMaxPixelForLinear(){
        var domain = this.domain();
        return [this(domain[0]), this(domain[1])];
    }
    function getDatatypeBasedScale(dataType, min, max){
        var scale;
        if (dataType == "string"){
            scale = d3.scale.ordinal().rangePoints([min, max], 0.5);
            scale.getBrushForDomain = getBrushForDomainForOrdinal;
            scale.getMinMaxPixel = getMinMaxPixelForOrdinal;
            scale.isOrdinal = true;
            return scale;
        }
        scale =  d3.scale.linear().range([min, max]);
        scale.getBrushForDomain = getBrushForDomainForLinear;
        scale.getMinMaxPixel = getMinMaxPixelForLinear;
        scale.isOrdinal = false;
        return scale;
    }
    x = getDatatypeBasedScale(dataTypes.xAxis, 0, width);
    x.isY = false;
    y = getDatatypeBasedScale(dataTypes.yAxis, height, 0);
    y.isY = true;
    size = d3.scale.linear().range([2.5, 15]);
    if (dataTypes.bubbleSize == null){
        size = d3.scale.linear().range([10,10]);
    }
    color = d3.scale.category20();
    xAxis = d3.svg.axis().scale(x).orient("bottom");
    yAxis = d3.svg.axis().scale(y).orient("left");
    brush = d3.svg.brush()
            .x(x).y(y)
            .on("brush", brushing)
            .on("brushend", brushend);
    svg = d3.select(targetSelector).append("svg:svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", "0 0 " + (width + margin[1] + margin[3]) + " "+ (height + margin[0] + margin[2]))
        .append("svg:g")
        .attr("transform", "translate(" + margin[3] + "," + margin[0] + ")");

    brushingObserver.registerListener(function(newChartRowIndex){
        chartRowIndex = newChartRowIndex;
        targetSelector = '#vis-row' + chartRowIndex + ' .vis'; // workaround
    }, chartRowIndex, function(selectedData){
        brush.clear();
        svg.selectAll('.brush').call(brush);
        //console.log('callback data changed... ');
        if (dots == undefined)
            dots = svg.selectAll('.dot');
        if (selectedData == null){
            dots.classed("notselected", function() { return false; });
            return;
        }
        charting.setSelectedProperty(dots, selectedData, channelMappings);
        dots.classed("notselected", function(d) { return !d.selected; });
    }, function(selectedDimensions){
        brush.clear();
        svg.selectAll('.brush').call(brush);

        if (selectedDimensions == null){
            if (dots) dots.classed("notselected", function() { return false; });
        } else {
            var brushXFrom, brushXTo, brushYFrom, brushYTo;

            var xChannel = charting.getChannelMappingForChannel(channelMappings, "x-Axis");
            var xSelectedDimension = charting.getDimensionByUri(selectedDimensions, xChannel.uri);
            if (xSelectedDimension != null){
                if (xSelectedDimension.from != null){
                    brushXFrom = x.getBrushForDomain(xSelectedDimension.from);
                    brushXTo = x.getBrushForDomain(xSelectedDimension.to);
                } else if (xSelectedDimension.values){

                }
            }

            var yChannel = charting.getChannelMappingForChannel(channelMappings, "y-Axis");
            var ySelectedDimension = charting.getDimensionByUri(selectedDimensions, yChannel.uri);
            if (ySelectedDimension != null && ySelectedDimension.from != null){
                brushYFrom = y.getBrushForDomain(ySelectedDimension.from);
                brushYTo = y.getBrushForDomain(ySelectedDimension.to);
                // Y is defined with 0/0 on the upper left corner. so flip from & to, if isOrdinal
                if (y.isOrdinal){
                    var tmpBrushYFrom = brushYFrom;
                    brushYFrom = brushYTo;
                    brushYTo = tmpBrushYFrom;
                }
            }

            var colorSelectedDimension = charting.getDimensionByUri(selectedDimensions, charting.getChannelMappingForChannel(channelMappings, "Color").uri);
            if (colorSelectedDimension != null)
                setSelectedFromColor(colorSelectedDimension);

            // brushed on X and Y:
            var extent = [[brushXFrom,brushYFrom],[brushXTo,brushYTo]];

            // only X or Y?
            if (brushXFrom && !brushYFrom){
                var minMaxY = y.isOrdinal ? y.getMinMaxPixel() : y.domain();
                extent = [[brushXFrom, minMaxY[0]], [brushXTo, minMaxY[1]]]; // to be considered: maxY = 0
            }
            if (!brushXFrom && brushYFrom){
                var minMaxX = x.isOrdinal ? x.getMinMaxPixel() : x.domain();
                extent = [[minMaxX[0], brushYFrom], [minMaxX[1], brushYTo]];
            }
            if (!extent[0][0] && !extent[0][1] && !extent[1][0] && !extent[1][1] && (xSelectedDimension != null || ySelectedDimension != null))
                setSelectedFromValues(xSelectedDimension, ySelectedDimension);
            else
                setSelectedFromExtend(extent, false);
        }
    });

    function setSelectedFromExtend(extent, doUpdateBrushingListeners) {
        if (dots == undefined)
            dots = svg.selectAll('.dot');
        if (extent[0][0] != extent[1][0] || extent[0][1] != extent[1][1]){ // if selectionArea is not empty
            setSelected(dots, extent);
            if (doUpdateBrushingListeners)
                updateBrushingListeners();
        }
    }

    function setSelectedFromValues(selectedDimensionX, selectedDimensionY) {
        if (dots == undefined)
            dots = svg.selectAll('.dot');
        if (selectedDimensionX != null || selectedDimensionY != null)
            dots.each(function(dot) {
                if (dot) {
                    var xIsInRange = selectedDimensionX == null || (_.contains(selectedDimensionX.values, dot.xAxis));
                    var yIsInRange = selectedDimensionY == null || (_.contains(selectedDimensionY.values, dot.yAxis));
                    dot.selected = xIsInRange && yIsInRange;
                }
            });
        dots.classed("notselected", function(d) { return !d.selected; });
    }

    function setSelectedFromColor(selectedDimension) {
        if (dots == undefined)
            dots = svg.selectAll('.dot');
        if (selectedDimension.from != null && selectedDimension.to != null){
            dots.each(function(dot) {
                if (dot)
                    dot.selected = (dot.bubbleColor >= selectedDimension.from && dot.bubbleColor <= selectedDimension.to);
            });
        } else if (selectedDimension.values != null){
            dots.each(function(dot) {
                if (dot)
                    dot.selected = _.contains(selectedDimension.values, dot.bubbleColor);
            });
        }
        dots.classed("notselected", function(d) { return !d.selected; });
    }

    function setSelected(dots, originalExtend) {
        dots.each(function(dot) {
            if (dot) {
                var xIsInRange = originalExtend[0][0] <= (x.isOrdinal ? x(dot.xAxis) : dot.xAxis)
                    && originalExtend[1][0] >= (x.isOrdinal ? x(dot.xAxis) : dot.xAxis);
                var yIsInRange = originalExtend[0][1] <= (y.isOrdinal ? y(dot.yAxis) : dot.yAxis)
                    && originalExtend[1][1] >= (y.isOrdinal ? y(dot.yAxis) : dot.yAxis);
                dot.selected = xIsInRange && yIsInRange;
            }
        });
        dots.classed("notselected", function(d) { return !d.selected; });
    }

    function brushing() {
        setSelectedFromExtend(brush.extent(), true);
    }

    function brushend() {
        var extent = brush.extent();
        if (extent[0][0] == extent[1][0] || extent[0][1] == extent[1][1]){ // if selectionArea is empty
            dots.classed("notselected", function() { return false; });
            dots.each(function(dot){ dot.selected = false;});
            brushingObserver.updateEmpty(chartRowIndex);
            return;
        }
        updateBrushingListeners();
        //debugBrushed(brush.extent());
    }

    function getBrushDimensions(selectedRawDots, extend){
        var selectedDimensions = [];

        if (selectedRawDots == null || selectedRawDots.length == 0)
            return selectedDimensions;

        var xMapping = charting.getChannelMappingForChannel(channelMappings, 'x-Axis');
        var dimensionX = {
            from: d3.min(selectedRawDots, function(d){return d.xAxis;}),
            to: d3.max(selectedRawDots, function(d){return d.xAxis;}),
            uri: xMapping.uri,
            label: xMapping.label,
            type: xMapping.type
        };
        if (dataTypes.xAxis != "string"){
            dimensionX.from = extend[0][0];
            dimensionX.to = extend[1][0];
        }
        selectedDimensions.push(dimensionX);

        var yMapping = charting.getChannelMappingForChannel(channelMappings, 'y-Axis');
        var dimensionY = {
            from: d3.min(selectedRawDots, function(d){return d.yAxis;}),
            to: d3.max(selectedRawDots, function(d){return d.yAxis;}),
            uri: yMapping.uri,
            label: yMapping.label,
            type: yMapping.type
        };
        if (dataTypes.yAxis != "string"){
            dimensionY.from = extend[0][1];
            dimensionY.to = extend[1][1];
        }
        selectedDimensions.push(dimensionY);

        return selectedDimensions;
    }

    function updateBrushingListeners(){
        var dotsSelected = [];
        dots.each(function(dot) { if (dot.selected) dotsSelected.push(dot); });
        var selectedRawData = _.map(dotsSelected, function(dot) { return charting.getRawDataFromVisObject(dot, channelMappings); });
        var selectedDimensions = getBrushDimensions(dotsSelected, brush.extent());
        brushingObserver.update(chartRowIndex, selectedRawData, selectedDimensions);
    }

    function comparator(a,b){
        if (a < b) return -1;
        if (a > b) return 1;
        return 0;
    }

    function getValue(value, datatype){
        if (datatype == "string")
            return value;
        return +value;
    }

    var drawVisualization = function(datarows) {

        // Map raw Data to Chart-Structure
        var data = [];
        var channelMappingLength = channelMappings.length;
        for(var i= 0, max = datarows.length; i<max; i++){
            var d = datarows[i];
            // Math.random()
            var newObj = { bubbleSize:1, bubbleColor:'' }; // bubbleSize and color are optional.
            for(var j= 0; j<channelMappingLength; j++){
                if (channelMappings[j].channel == 'x-Axis'){
                    newObj.xAxis = getValue(d[j], channelMappings[j].datatype);
                } else if (channelMappings[j].channel == 'y-Axis'){
                    newObj.yAxis = getValue(d[j], channelMappings[j].datatype);
                } else if (channelMappings[j].channel == 'Color'){
                    newObj.bubbleColor = d[j];
                } else if (channelMappings[j].channel == 'Size'){
                    newObj.bubbleSize = parseFloat(d[j].replace(/,/g,''));
                }
            }
            if (newObj.bubbleSize > 0)
                data.push(newObj);
        }

        // sort data by color, to get a overall-equal mapping of the legend.
        data = _.sortBy(data, function(dataObject){return dataObject.bubbleColor});
        color.domain(_.map(data, function(dataObject){ return dataObject.bubbleColor; }));

        //data = [];
        //data.push({bubbleSize:0.5, bubbleColor:'test1', xAxis:2007, yAxis:500000});
        //data.push({bubbleSize:0.5, bubbleColor:'test2', xAxis:2011, yAxis:10000});
        //data.push({bubbleSize:0.5, bubbleColor:'test3', xAxis:2017, yAxis:20000});
        //data.push({bubbleSize:0.5, bubbleColor:'test4', xAxis:2011, yAxis:50000});
        //data.push({bubbleSize:0.5, bubbleColor:'test5', xAxis:2012, yAxis:600000});
        //data = [];
        //data.push({bubbleSize:0.5, bubbleColor:'test5', xAxis:2012, yAxis:600000});
        //data.push({bubbleSize:0.5, bubbleColor:'test4', xAxis:2011, yAxis:50000});
        //data.push({bubbleSize:0.5, bubbleColor:'test3', xAxis:2017, yAxis:20000});
        //data.push({bubbleSize:0.5, bubbleColor:'test2', xAxis:2011, yAxis:10000});
        //data.push({bubbleSize:0.5, bubbleColor:'test1', xAxis:2007, yAxis:500000});

        if (dataTypes.xAxis == "string")
            x.domain(data.map(function(d) { return d.xAxis; }).sort(comparator));
        else
            x.domain(d3.extent(data, function(d) { return d.xAxis; })).nice();

        if (dataTypes.yAxis == "string")
            y.domain(data.map(function(d) { return d.yAxis; }).sort(comparator));
        else
            y.domain(d3.extent(data, function(d) { return d.yAxis; })).nice();

        size.domain(d3.extent(data, function(d) { return d.bubbleSize; })).nice();


        svg.append("g")
            .attr("class", "brush")
            .call(brush);

        svg.selectAll(".dot")
            .data(data)
            .enter().append("circle")
            .attr("class", "dot").style("opacity", .8)
            //.attr("r", 3.5)
            .attr("r", function(d){
                return size(d.bubbleSize);
            })
            .attr("data-r", function(d){
                return size(d.bubbleSize);
            })
            .attr("cx", function(d) { return x(d.xAxis); }) //???
            .attr("cy", function(d) { return y(d.yAxis); }) //???
            .style("fill", function(d) { return color(d.bubbleColor); })
            .on("mouseover", circleMouseOver)
            .on("mouseout", circleMouseOut)
            .append("title")
            .text(function(d) { if (Vis.config.debug) { return d.bubbleColor + ' - ' + d.bubbleSize + ' - ' + d.xAxis + ' - ' + d.yAxis;} return d.bubbleColor; });

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

        var legend = svg.selectAll(".legend")
            .data(color.domain())
            .enter().append("g")
            .attr("class", "legend")
            .attr("transform", function(d, i) { return "translate(0," + i * 16 + ")"; });

        legend.append("rect")
            .attr("x", width + margin[1] - 20)
            .attr("width", 18)
            .attr("height", 13)
            .style("fill", color);

        legend.append("text")
            .attr("x", width + margin[1] - 25)
            .attr("y", 5)
            .attr("dy", ".35em")
            .style("text-anchor", "end")
            .text(function(d) { return d; });

        $(".dot").tipsy({ gravity: 's' });
    };

    var circleMouseOver = function() {
        var circle = d3.select(this);

        // transition to increase size/opacity of bubble
        circle.transition()
            .duration(800).style("opacity", 1)
            .attr("r", +circle.attr("data-r") + 10).ease("elastic");

        // function to move mouseover item to front of SVG stage, in case
        // another bubble overlaps it
        d3.selection.prototype.moveToFront = function() {
            return this.each(function() {
                this.parentNode.appendChild(this);
            });
        };

        // skip this functionality for IE9, which doesn't like it
        if (!$.browser.msie) {
            circle.moveToFront();
        }
    };
// what happens when we leave a bubble?
    var circleMouseOut = function() {
        var circle = d3.select(this);
        //console.log('datar: ' + circle.attr("data-r"));

        // go back to original size and opacity
        circle.transition()
            .duration(800).style("opacity", .8)
            .attr("r", circle.attr("data-r")  ).ease("elastic");
    };

    drawVisualization(datarows);

    //debug();
};