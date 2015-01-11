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

var scatterplotmatrix = function (dataInput, channelMappings, targetSelector, chartRowIndex){
    var width = 900,
        size = 150,//150,
        padding = 30,//19.5,
        legendwidth = 200,
    	left = 100+legendwidth;
    	
    
    var x = d3.scale.linear()
        .range([padding / 2, size - padding / 2]);
    var xY = d3.scale.linear()
        .range([padding / 2, size - padding / 2]);
        
    var y = d3.scale.linear()
        .range([size - padding / 2, padding / 2]);
    var yY = d3.scale.linear()
        .range([size - padding / 2, padding / 2]);
    
    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom")
        .ticks(5);
    var xAxisY = d3.svg.axis()
        .scale(xY)
        .orient("bottom")
        .ticks(5);
    
    
    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .ticks(5);
    var yAxisY = d3.svg.axis()
        .scale(yY)
        .orient("left")
        .ticks(5);
    
    var dots;
     
    //var color = d3.scale.category20();

    var sortedDictionaries = {};
    //daten.json
    var drawVisualization = function(dataInput, targetSelector) {
    //d3.json(dataUrl, function(data) {

        data = dataInput.slice(0,-1);
        sortedDictionaries = dataInput[dataInput.length-1];
        
    	var domainByTrait = {},
          traits = d3.keys(data[0]);
    	  //.filter(function(d) {
    	//	  return d !== "species";
    	//	  }),
          n = traits.length;
    	  
    	traits.forEach(function(trait) {
    		domainByTrait[trait] = d3.extent(data, function(d) {
    		return d[trait]; 
    		});
      });
    	  
    	  
      xAxis.tickSize(size * n);
      xAxisY.tickSize(size * n);
      yAxis.tickSize(-size * n);
      yAxisY.tickSize(-size * n);
      

      var brush = d3.svg.brush()
          .x(x)
          .y(y)
          .on("brushstart", brushstart)
          .on("brush", brushmove)
          .on("brushend", brushend);
    

          
      var svg = d3.select(targetSelector).append("svg")
          .attr("class", "scatterplotmatrix")
          //.attr("width", size * n + padding+left)
          //.attr("height", size * n + padding+padding*2)// x Axis vertical values
          .attr("width", "100%")
          .attr("height", "100%")
          .attr("viewBox", "0 0 " + (size * n + padding+left) + " "+ (size * n + padding+padding*2))
          .append("g")
          .attr("transform", "translate(" + (padding+left) + "," + padding / 2 + ")");    
    
    
      svg.selectAll(".x.axis")
          .data(traits)
          .enter().append("g")
          .attr("class", "x axis")
          .attr("transform", function(d, i) { return "translate(" + (n - i - 1) * size + ",0)"; })
          .each(function(d) { 
              if(d=="Year")
              {
                  xY.domain(domainByTrait[d]); 
                  d3.select(this).call(xAxisY.tickFormat(d3.format("04d"))); 
              }
              else
              {
                  x.domain(domainByTrait[d]); 
                  d3.select(this).call(xAxis);
              } 
              });
    
      svg.selectAll(".x.axis text")
          .attr("transform", function(d) {
              return "translate(" + -(size * n +5)+"," + ((size * n)+15) + ") rotate(-90)";
              });
    
      svg.selectAll(".y.axis")
          .data(traits)
          .enter().append("g")
          .attr("class", "y axis")
          .attr("transform", function(d, i) { return "translate(0," + i * size + ")"; })
          .each(function(d) { 
              if(d=="Year")
              {
                yY.domain(domainByTrait[d]); 
                d3.select(this).call(yAxisY.tickFormat(d3.format("04d"))); 
              }
              else
              {
                y.domain(domainByTrait[d]); 
                d3.select(this).call(yAxis);  
              }
              });
    
    	  
      var cell = svg.selectAll(".cell")
          .data(cross(traits, traits))
          .enter().append("g")
          .attr("class", "cell")
          .attr("transform", function(d) { return "translate(" + (n - d.i - 1) * size + "," + d.j * size + ")"; })
          .each(plot);
    
      // Titles for the diagonal.
      cell.filter(function(d) { return d.i === d.j; }).append("text")
          .attr("x", padding)
          .attr("y", padding)
          .attr("dy", ".71em")
          .attr("class",function(d,i){return "l"+i})
          .text(function(d) { return d.x; })
          .on('click', function(d,i){
                Vis.view.getNewAxisLabel(d.x, function(newAxisLabel){
                    cell.select(".l"+i).text(newAxisLabel); 
                    });
            });
    
    //receive data from another diagrams	  
    brushingObserver.registerListener(function(newChartRowIndex){
        chartRowIndex = newChartRowIndex;
        targetSelector = '#vis-row' + chartRowIndex + ' .vis'; // workaround
    }, chartRowIndex, function(selectedData){
        cell.call(brush.clear());
        svg.selectAll('.brush').call(brush);
        
        //console.log('callback data changed... ');
        if (dots == undefined){
            dots = svg.selectAll('.dot');
        }
        if (selectedData == null){
            dots.classed("hidden", function(d) { return false; });
            return;
        }
        dots.each(function(dot) {
            if (dot) {
                
                //hard code year-number as string
                /*
                if(dot.hasOwnProperty("Year")){
                    dot["Year"] = dot["Year"].toString();
                }
                   */
                var compareArray = [];
                // get key-data to value-data
                channelMappings.forEach(function(element){
                    currentElement = element["label"];
                    if(sortedDictionaries.hasOwnProperty(currentElement)){
                        compareArray.push(sortedDictionaries[currentElement][dot[currentElement]]);
                    }else{
                        compareArray.push(dot[currentElement]);
                    }
                });
                

                dot.selected = false;
                for(var i= 0, max=selectedData.length; i<max; i++){
                    if (selectedData[i].compare(compareArray))//dot
                        dot.selected = true;
                }
            }
            
        });
        
        dots.classed("hidden", function(d) { return !d.selected; });
        
    }, function(selectedDimensions){
        cell.call(brush.clear());
        svg.selectAll('.brush').call(brush);
        
        if (dots == undefined){
            dots = svg.selectAll('.dot');
        }
        if (selectedDimensions == null){
            //if (dots) dots.classed("notselected", function(d) { return false; });
            dots.classed("hidden", function(d) { return false; });
            return;
        }
        
        var dictDemension = {};
        selectedDimensions.forEach(function(element){
            dictDemension[element.label] = {
                "from":element.from,
                "fromValue":element.from != null && sortedDictionaries.hasOwnProperty(element.label)?
                    Object.keys(sortedDictionaries[element.label]).filter(function(key){
                        return sortedDictionaries[element.label][key]== element.from;
                        })[0]:"NoData",
                "to":element.to,
                "toValue":element.to != null && sortedDictionaries.hasOwnProperty(element.label)?
                    Object.keys(sortedDictionaries[element.label]).filter(function(key){
                        return sortedDictionaries[element.label][key]== element.to;
                        })[0]:"NoData",
                "values": element.values != null && sortedDictionaries.hasOwnProperty(element.label)?
                    Object.keys(sortedDictionaries[element.label]).filter(function(key){
                        return _.contains(element.values, sortedDictionaries[element.label][key]);
                        }):null
                };
        });
        
        /*
        var inputDataFromIntervall = [];
        for(var i=0; i<selectedDimensions.length; i++){
            for(var j=0; j<channelMappings.length; j++){
                if (channelMappings[j].label == selectedDimensions[i].label){
                    if (channelMappings[j].channel == 'axis'){

                    }
                }
            }
        }
        */
        
        dots.each(function(dot) {
            if (dot) {
               
                dot.selected = false;  
                //var compareArray = [];
                // get key-data to value-data
                
                var comparedCount = 0; 
                Object.keys(dictDemension).forEach(function(key){
                    if(dictDemension[key].from != null){
                        if(dictDemension[key].fromValue == "NoData"){
                            if( parseFloat(dictDemension[key].from) <= dot[key] &&
                                dot[key] <= parseFloat(dictDemension[key].to) ){
                                comparedCount++;
                            }
                        } else {
                            if( parseFloat(dictDemension[key].fromValue) <= dot[key] &&
                                dot[key] <= parseFloat(dictDemension[key].toValue) ){
                                comparedCount++;
                            }
                        }
                    } else if (dictDemension[key].values != null) {
                        if (_.contains(dictDemension[key].values, parseFloat(dictDemension[key].fromValue))) {
                            comparedCount++;
                        }
                    }
                });
                if(Object.keys(dictDemension).length == comparedCount){
                    dot.selected = true; 
                }
                
                /*
                channelMappings.forEach(function(element){
                    currentElement = element["label"];
                    if(sortedDictionaries.hasOwnProperty(currentElement)){
                        if(dictDemension.hasOwnProperty(currentElement)){
                            //console.log(dictDemension[currentElement].fromValue + " <= " + dot[currentElement] + " <= " +dictDemension[currentElement].toValue);
                            if( parseFloat(dictDemension[currentElement].fromValue) <= dot[currentElement] &&
                                dot[currentElement] <= parseFloat(dictDemension[currentElement].toValue) ){
                                dot.selected = true;   
                                //compareArray.push(dot[currentElement]); 
                            }
                        }
 
                        // compareArray.push(sortedDictionaries[currentElement][dot[currentElement]]);
                    }else{
                        if(dictDemension.hasOwnProperty(currentElement)){
                            if( parseFloat(dictDemension[currentElement].from) <= dot[currentElement] &&
                                dot[currentElement] <= parseFloat(dictDemension[currentElement].to) ){
                                dot.selected = true;   
                                //compareArray.push(dot[currentElement]); 
                            }
                        }
                        //compareArray.push(dot[currentElement]);  
                    }
                });
                */
                
                           /*   
                var testData =[];
                //testData.push(["jayapal","Recall"]);
                testData.push(["jayapal"]);
                
                //compareArray = [];compareArray[0]="jayapal";compareArray[1]="Recall";
               compareArray.pop();
               compareArray.pop();

                
                dot.selected = false;       
                for(var i= 0, max=testData.length; i<max; i++){
                    if (testData[i].compare(compareArray)){//dot
                        dot.selected = true;
                    }
                }
                */
            }
            
        }); 
        
        
        dots.classed("hidden", function(d) { return !d.selected; });

    });    	  
    	  
    	  
    function plot(p) {
        var cell = d3.select(this);
         
        x.domain(domainByTrait[p.x]);
        y.domain(domainByTrait[p.y]);
        
        cell.append("rect")
            .attr("class", "frame")
            .attr("x", padding / 2)
            .attr("y", padding / 2)
            .attr("width", size - padding)
            .attr("height", size - padding);
        
        cell.selectAll("circle")
            .data(data)
            .enter().append("circle")
            .attr("cx", function(d) { return x(d[p.x]); })
            .attr("cy", function(d) { return y(d[p.y]); })
            .attr("r", 3)
            .attr("class","dot");
            //.style("fill", function(d) { return color(d.species); });//without color
        
        		
        cell.call(brush);
    }

    
    var brushCell;

    // Clear the previously-active brush, if any.
    function brushstart(p) {
        if (brushCell !== p) {
            cell.call(brush.clear());
            x.domain(domainByTrait[p.x]);
            y.domain(domainByTrait[p.y]);
            brushCell = p;
        }
    }

     // Highlight the selected circles.
     // And send selected data to another diagrams.
    function brushmove(p) {
        var selectedRawData = [];
        
        var selectedArray = [];
        
        var e = brush.extent();
        
       
        var resultMapping = function(val){return channelMappings.filter(function(element){return element.label == val;})[0]};
        var dimensionX = {
            from: Number.MAX_VALUE,
            to: 0.0,
            uri: resultMapping(p.x).uri,
            label: p.x,
            type: resultMapping(p.x).type
        };
        var dimensionY; 
        if(p.x != p.y){
            dimensionY = {
                from: Number.MAX_VALUE,
                to: 0.0,
                uri: resultMapping(p.y).uri,
                label: p.y,
                type: resultMapping(p.y).type
            };
        }
        
        var CompareValue = function(cmpObj1,operator,cmpObj2,cmpSubObj2){
            
            if(operator == "<" && cmpObj1 < cmpObj2[cmpSubObj2]){
                cmpObj2[cmpSubObj2] = cmpObj1;
            }
            if(operator == ">" && cmpObj1 > cmpObj2[cmpSubObj2]){
                cmpObj2[cmpSubObj2] = cmpObj1;
            }
            
        };
        
        svg.selectAll("circle").classed("hidden", function(d) {
            
            var condition = e[0][0] > d[p.x] || d[p.x] > e[1][0]
                || e[0][1] > d[p.y] || d[p.y] > e[1][1];

            //Collect data from selected.
            if(!condition){
                var currentElement = null;
                channelMappings.forEach(function(element){
                    currentElement = element["label"];
                    
                    if(p.x == element.label){
                        CompareValue(d[element.label] ,"<", dimensionX,"from");
                        CompareValue(d[element.label] ,">", dimensionX,"to");
                    }
                    if(p.x != p.y && p.y == element.label){
                        CompareValue(d[element.label] ,"<", dimensionY,"from");
                        CompareValue(d[element.label] ,">", dimensionY,"to");
                    }
                    
                    if(sortedDictionaries.hasOwnProperty(currentElement)){
                        selectedArray.push(sortedDictionaries[currentElement][d[currentElement]]);
                    }else{
                        var data = d[currentElement];
                        //hardcoded
                        if(currentElement == "Year"){
                            data = data.toString();
                        }
                        selectedArray.push(data);
                    }
                });
                
                selectedRawData.push(selectedArray);
                selectedArray = [];
            
            }   
            return condition; 
        });
        
        var selectedDimensions = [];
        
        
        if(sortedDictionaries.hasOwnProperty(dimensionX.label)){
            var valueToNameObjX = sortedDictionaries[dimensionX.label];
            dimensionX.from = valueToNameObjX[dimensionX.from];
            dimensionX.to = valueToNameObjX[dimensionX.to];
        }
        if(p.x != p.y && sortedDictionaries.hasOwnProperty(dimensionY.label)){
            var valueToNameObjY = sortedDictionaries[dimensionY.label];
            dimensionY.from = valueToNameObjY[dimensionY.from];
            dimensionY.to = valueToNameObjY[dimensionY.to];
        }
        
        selectedDimensions.push(dimensionX);    
        if(p.x != p.y){
            selectedDimensions.push(dimensionY); 
        }
            
        if(selectedRawData.length != 0){    
            //brushingObserver.update(chartRowIndex, selectedRawData);
            brushingObserver.update(chartRowIndex, selectedRawData, selectedDimensions);
            //console.log(selectedRawData);
            //console.log(p);
            
        }else{
            brushingObserver.update(chartRowIndex, null);   
            brushingObserver.updateEmpty(chartRowIndex);
        }
        
    }
    
    // If the brush is empty, select all circles.
    function brushend() {
        if (brush.empty()) svg.selectAll(".hidden").classed("hidden", false);
    }

      
      
    function cross(a, b) {
        var c = [], n = a.length, m = b.length, i, j;
        for (i = -1; ++i < n;) for (j = -1; ++j < m;) c.push({x: a[i], i: i, y: b[j], j: j});
        return c;
    }
        
    //d3.select(self.frameElement).style("height", size * n + padding +left+ 20 + "px");
    d3.select(self.frameElement).style("height", size * n + padding + 20 + "px");
    
    //make data for legends
    var stringArray = [];
    for(var element in sortedDictionaries)
    {

        stringArray.push(" ");
        stringArray.push("# " +element);
        
        for(var e in sortedDictionaries[element])
        {
            stringArray.push(e + ":" + sortedDictionaries[element][e]);
        }
    }
    
    function stringCut(str,maxlen){
        var returnString = str;
        if(str.length > maxlen){
            returnString = str.substring(0,maxlen) + "...";
        }
        return returnString;
    }
    
    //make legends
    var legend = svg.selectAll(".legend")
        .data(stringArray)
        //.data(color.domain().slice().reverse())
        .enter().append("g")
        .attr("class", "legend")
        .attr("transform", function(d, i) { return "translate(0," + i * 10 + ")"; });

    
    legend.append("text")
        .attr("x", -legendwidth)
        .attr("y", 9)
        .attr("dy", ".35em")
        .style("text-anchor", "begin")
        .text(function(d) { return stringCut(d,20); })
        .append("title")
        .text(function(d) { return d; });

    }
    
    drawVisualization(dataInput, targetSelector);
}