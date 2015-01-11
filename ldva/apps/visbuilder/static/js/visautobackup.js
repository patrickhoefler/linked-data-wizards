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

var dataUrlBase = "/viz?cmd=getD3Data";
var dataUrl;

var globals={
	     cachedChart:"",
	     cachedDimension: "",
	     dimensionUri : "",
	     mappingArray : [], 
	     chartArray : [],
	     dimensionArray : [],
	     dataset : "",
	     chartUri : "",
	     visualChannelInfo : [],
	     switchArray: []
	     };

$(document).ready(function () {
    $.address.externalChange(external_address_change_handler); // Sobald sich die adresse ändert wird die fkt external_address_change_handler aufgerufen
    $("#selectable3").selectable({
    	stop: function(){
            $(".ui-selected", this).each(function(){
            	globals.cachedChart= this.id;
            	globals.chartUri = $(this).attr("charturi");
            	
            	var visChannels = "";
            	//console.log (globals.visualChannelInfo);
            	for (var k = 0; k<globals.visualChannelInfo.length; k++){
            		var ch = globals.visualChannelInfo[k].chart;
            		if (ch == globals.cachedChart ){
            			
            			var vischannels = globals.visualChannelInfo[k].visualChannels;
            			for (var l = 0; l<vischannels.length; l++){
            				if(globals.dimensionArray.length != 1){
            					if (vischannels[l] != "y-Axis"){
            					visChannels = visChannels+'<li id="'+vischannels[l]+'"class="ui-widget-content">'+vischannels[l]+'</li>'; 
            					}
                         	}
							if(vischannels [l]==null){
							     alert("Dimension can not be showed");
							     return;
							}
         	                
                       
							$("#selectable4").html(visChannels);
            			}
            			
            			
            		}
            	
            		
            	}
            	getVisualization(globals.cachedChart);
            	/*if (globals.mappingArray.length == 1){
            		globals.cachedChart = "";
            		getVisualization (globals.cachedChart, decodeURIComponent(globals.dataset));
            		
            	}*/
            	
            	
            });
        },
     selecting:function() {
    	$(".ui-selected", this).each(function(){
    	$(this).toggleClass("ui-selected");
    	});
      }	
    });

   /*$("#selectable1").selectable({
    	stop: function(){
            $(".ui-selected", this).each(function(){
            	var cachedDimension = this.id;
            	var dimensionUri = $(this).attr("dimensionuri");
            	var mappingObject = {'dim':cachedDimension , 'dimensionuri':dimensionUri};
            	globals.mappingArray.push(mappingObject); 
            	console.log (globals.mappingArray);
            });
        },*/
        
    $("#selectable1").selectable({
    	stop: function(){
            $(".ui-selected", this).each(function(){
            	globals.cachedDimension = this.id;
            	globals.dimensionUri = $(this).attr("dimensionuri");
            	selectDim(globals.cachedDimension, globals.dimensionUri);

            });
            
            
    	 },
        
     selecting:function() {
    	$(".ui-selected", this).each(function(){
    	$(this).toggleClass("ui-selected");
    	});
      }	
    });
    
    $("#selectable4").selectable({
    	stop: function(){
            $(".ui-selected", this).each(function(){

            	globals.cachedVisualChannel = this.id;



            });
            
            
    	 },
        
     selecting:function() {
    	$(".ui-selected", this).each(function(){
    	$(this).toggleClass("ui-selected");
    	});
      }	
    });
    $("#preview").button();

    $("#preview").click(
    		function(){
    			getVisualization(globals.cachedChart, decodeURIComponent(globals.dataset));	
    			
    			
    		}
    		);
    $("#switch").button();

    $("#switch").click(
    		function(){
    			
    			switchDimension();
			
    		}
    		);
    $("#map").button();

    $("#map").click(
    		function(){
    			
    			putMapEntry();
			
    		}
    		);
    
    
});
	


function external_address_change_handler(event){
    var value, dataset, chart, chartid;
    if (event.parameterNames.length > 0) {
    	$("#vis").html();
        
        $("#demo2").html('');
        $("#demo2Up").html('');
        $("#selectable4").html('');	
        $("#selectable3").html('');	
        $("#selectable2").html('');
        $("#selectable1").html('');
       
        
        
        
        for (key in event.parameters) {
            value = event.parameters[key];
            if (key == "dataset"){
                globals.dataset = value;
            } 
        }
        if (dataset == ""){
            alert('Parameter list not correct');
            return;
        }

      getPreview();
    }
}




function selectDim(cachedDimension, dimensionUri){
	globals.mappingArray = []; 
	
	var mappingObject = {'dim':cachedDimension , 'dimensionuri':dimensionUri};
	globals.mappingArray.push(mappingObject); 
	//console.log(globals.dimensionArray);
	if (globals.cachedChart == "parallelcoordinates"){
		for (var i = 0; i<globals.dimensionArray.length;i++){
			
			var lab = globals.dimensionArray[i].label;
			var dimensionUri = globals.dimensionArray[i].dimensionuri;
			if (lab != cachedDimension){
				var mappingObject2 = {'dim':lab,'dimensionuri':dimensionUri };
				globals.mappingArray.push(mappingObject2);
				//console.log(globals.mappingArray);
			}
				
		}
		
	}
	

	//console.log(globals.mappingArray);
	//globals.mappingArray = [];
}

function getPreview (){
    var start=null;
    globals.chartArray = [];
    //console.log(decodeURIComponent(globals.dataset));
    $.post("/viz", { cmd: "getPreviewAuto", chart:'', dataset:decodeURIComponent(globals.dataset), dimension:''},
        function(dt) {
            var charts="";
            $("#vis").html();
            $("#vis").html("<canvas id='background'></canvas><canvas id='foreground'></canvas>");
            $("#demo2").html('');
            $("#demo2Up").html('');
            $("#selectable2").html('');
            $("#selectable3").html('');
          
            globals.visualChannelInfo = dt;  // Um die visual channel(s) vom supportedchart(s) zu erhalten
            for(var x = 0; x < dt.length; x++){
            	var ch = dt[x].chart;
            	var churi = dt[x].charturi;
            	globals.chartArray.push(ch);
            	//alert(ch);
                charts = charts+'<li id="'+ch+'" charturi="'+churi+'" class="ui-widget-content">'+ch+'</li>';
                //console.log (charts);
                getDimensions();
                
              
            }
			$("#selectable3").html(charts);
    }, "json").error(function() {err("Error while showing supported charts."); });
			

    }
function getDimensions (){
	$.post("/viz", { cmd: "getDimension",  dataset:decodeURIComponent(globals.dataset)},
	        function(dt) {
			globals.dimensionArray = dt;
			getMeasure();
			//console.log(globals.dimensionArray);
			globals.mappingArray = [];
			globals.cachedChart = "";
			//globals.switchArray = [];
				$("#selectable2").html("");
				$("#vis").html();
	            $("#vis").html("<canvas id='background'></canvas><canvas id='foreground'></canvas>");
	            var dimensions = "";
	            for(var x = 0; x < dt.length; x++){
	            	//console.log (dt);
	                var dimension = dt[x].label;
	                var dimensionuri = dt[x].dimensionuri;
	                //globals.switchArray = dt;
	                //dimensions = dimensions+'<li id='+dimension+'dimensionuri='+dimensionuri+'class="ui-widget-content">'+dimension+'</li>';
	                if(dt.length != 1){
	                	dimensions = dimensions+'<li id="'+dimension+'" dimensionuri="'+dimensionuri+'" class="ui-widget-content">'+dimension+'</li>'; 
	                		
	                }
	                if(dimension==null){
	                    alert("Dimension can not be showed");
	                    return;
	                }
	                
	            }
	            if(dt.length == 1){
	            	var chart = "";
	            	
                	var mappingObject = {'dim':dimension , 'dimensionuri':dimensionuri};
                	globals.mappingArray.push(mappingObject);
                
            		chart = globals.chartArray [0];
            		//console.log (chart);
            		getVisualization(chart);
              }
	            $("#selectable1").html(dimensions);
	        }, "json")
	        .error(function() {alert("Error while loading dimensions."); });
	}

function getMeasure(){
	$.post("/viz", { cmd: "getMeasure",  dataset:decodeURIComponent(globals.dataset)},
	        function(dt) {
			//globals.dimensionArray= dt;
			globals.mappingArray = [];
			globals.cachedChart = "";
			$("#vis").html();
            $("#vis").html("<canvas id='background'></canvas><canvas id='foreground'></canvas>");
            var measures = "";
            for(var x = 0; x < dt.length; x++){
            	var measure = dt[x].label;
                var measureuri = dt[x].measureuri;	
                
                if(globals.dimensionArray.length != 1){
                	measures = measures+'<li id="'+measure+'" measurenuri="'+measureuri+'" class="ui-widget-content">'+measure+':y-Axis'+'</li>'; 
        	
                }
                if(measure==null){
                    alert("Dimension can not be showed");
                    return;
                }
	                
              }
	            $("#selectable2").html(measures);
	        }, "json")
	        .error(function() {alert("Error while loading dimensions."); });
	}


function getVisualization (cachedChart){
	
	if ((globals.mappingArray.length) > 0){
	console.log (globals.mappingArray);	
	 var start=null; 
	 
	 //console.log (cachedChart);
	   //$("#vis").html("<img src='/static/images/ajax-loader.gif' border='0'>");
	    $.post("/viz", { cmd: "getVisualization", chart:cachedChart, dataset:decodeURIComponent(globals.dataset), dimension:JSON.stringify(globals.mappingArray)},
	    		
	        function(dt) {
	            var conf =  'var config={location:"vis", height:"600", width:"700", title:"Generated chart"}';
	            var warn = null;
	            //$("#vis").html("");
	            $("#vis").html();
	            $("#vis").html("<canvas id='background'></canvas><canvas id='foreground'></canvas>");
	            $("#demo2").html('');
	            $("#demo2Up").html('');
	           		
	            for(var x = 0; x < dt.length; x++){
	            	
	                start = dt[x].start;
	                if(start==null){
	                    alert("Chart  could not be generated");
	                    return;
	                }
	                
	                eval(conf);
	                console.log(start);
	                eval(start);
	    
	                if (globals.mappingArray.length != 1){
	                globals.mappingArray = [];
	                }
	                
	            }
	           
	        
	        }, "json")
	        .error(function() {alert("Error while preparing preview."); });
	}
	else {
		console.log (cachedChart);
		for(var x = 0; x < globals.dimensionArray.length; x++){
        	//console.log (dt);
            var dimension = globals.dimensionArray[x].label;
            var dimensionuri = globals.dimensionArray[x].dimensionuri;
            var mappingObject = {'dim':dimension , 'dimensionuri':dimensionuri};
        	globals.mappingArray.push(mappingObject);
		
		}
		var start=null; 
		 
		 //console.log (cachedChart);
		   //$("#vis").html("<img src='/static/images/ajax-loader.gif' border='0'>");
		    $.post("/viz", { cmd: "getVisualization", chart:cachedChart, dataset:decodeURIComponent(globals.dataset), dimension:JSON.stringify(globals.mappingArray)},
		    		
		        function(dt) {
		            var conf =  'var config={location:"vis", height:"600", width:"700", title:"Generated chart"}';
		            var warn = null;
		            $("#vis").html();
		            $("#vis").html("<canvas id='background'></canvas><canvas id='foreground'></canvas>");
		            
		            for(var x = 0; x < dt.length; x++){
		            	
		                start = dt[x].start;
		                if(start==null){
		                    alert("Chart  could not be generated");
		                    return;
		                }
		                
		                eval(conf);
		                console.log(start);
		                eval(start);
		    
		                if (globals.mappingArray.length != 1){
		                globals.mappingArray = [];
		                
		               // Hier zeigen wir nun, welche dimension auf welche achse gemappt wurde
	                }
		                
		            }
		           
		        
		        }, "json")
		        .error(function() {alert("Error while preparing preview."); });
	
	}	
		
	
}

function switchDimension(){
	
	var i = 0;
	var dimensions = "";
	var newArray = []; 
	//console.log(globals.switchArray);
	for (i= (globals.dimensionArray.length)-1;i>=0; i--){
		var dimension = globals.dimensionArray[i].label;
        var dimensionuri = globals.dimensionArray[i].dimensionuri;
        dimensions = dimensions+'<li id="'+dimension+'" dimensionuri="'+dimensionuri+'" class="ui-widget-content">'+dimension+'</li>'; 
        var newObject = {'dimensionuri':dimensionuri, 'label': dimension };
        newArray .push(newObject);
		
	}
	globals.dimensionArray = newArray;
	$("#selectable1").html(dimensions);
	
	
}

function putMapEntry(){
	globals.mappingArray = [];
	if(globals.dimensionUri == null || globals.dimensionUri.length<1){
		alert("Dimension was not selected");
		return;
	}
		if(globals.cachedVisualChannel == null || globals.cachedVisualChannel.length<1){
			alert("Visual channel was not selected");
		return;
		}
		
		var mappingObject = {'dimensionuri': globals.dimensionUri, 'visualchannel': globals.cachedVisualChannel}
		for(var t = 0;t<globals.mappingArray.length;t++){
			var object = globals.mappingArray[t];

			var dimUri = object.dimensionuri;
			var visChannel = object.visualchannel;
			if(dimUri == globals.dimensionUri||visChannel == globals.cachedVisualChannel){
				alert("Duplicates are not allowed");
			return;
			}
		}
		globals.mappingArray.push(mappingObject);
	
		console.log(globals.mappingArray);
		
}


