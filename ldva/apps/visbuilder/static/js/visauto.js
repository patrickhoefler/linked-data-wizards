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
	     switchArray: [],
	     mappingInfoForVisualChannels: [],
	     cubeComponentArray : []
	    
	     };

$(document).ready(function () {
    $.address.externalChange(external_address_change_handler); 
    globals.mappingArray = [];
    $("#selectable3").selectable({
    	stop: function(){
            $(".ui-selected", this).each(function(){
            	globals.cachedChart= this.id;
            	globals.chartUri = $(this).attr("charturi");
            	
            	getPossibleVisualizationVariants ();
            	getVisualization();
            	
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
    			//console.log(globals.cachedChart);
    			globals.cubeComponentArray = [];
    			var visChannelArray = []
    			//console.log("global dimension uri");
    			//console.log(globals.dimensionArray);
    			getDimensions();
    			for (var i = 0; i<globals.dimensionArray.length;i++ ){
    				var dimuri = globals.dimensionArray[i].dimensionuri;
    				
    				var label = globals.dimensionArray[i].label;
    				var el = document.getElementById("vischannel"+i);
    				var visChannel= el.options[el.selectedIndex].text;
    				var visChannelObject = {'dimensionuri':dimuri, 'cubecomponent':visChannel, 'label':label, 'index':i};
    				visChannelArray.push(visChannelObject);
    				
    			}
    			globals.cubeComponentArray = visChannelArray
    			
    			getVisualization();	   			    			
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
        $("#suggestions").html('');
        
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

/*function selectDim(cachedDimension, dimensionUri){
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
}*/

function hasDuplicatedEntry( chartName, chartArray )
{
	for( var x=0; x<chartArray.length; x++ )
	{
		if ( chartArray[x] == chartName )
		{
			return true;
		}
	}
	return false;
}

function getPreview (){
    globals.chartArray = [];
    globals.visualChannelInfo = [];
    
    //console.log(decodeURIComponent(globals.dataset));
    //console.log(decodeURIComponent(globals.dataset));
    $.post("/viz", { cmd: "getPreviewAuto", chart:'', dataset:decodeURIComponent(globals.dataset), dimension:''},
        function(dt) {
    	//alert (dt.length);
            var charts="";
            $("#vis").html();
            
            $("#vis").html("<canvas id='background'></canvas><canvas id='foreground'></canvas>");
            $("#demo2").html('');
            
            $("#demo2Up").html('');
            $("#selectable2").html('');
            $("#selectable3").html('');
          
            globals.visualChannelInfo = dt;  // Um die visual channel(s) vom supportedchart(s) zu erhalten
            //console.log(dt);
            var chartArray = [];
            for(var x = 0; x < dt.length; x++){
            	globals.mappingInfoForVisualChannels = dt;
            	//console.log(dt);
            	var ch = dt[x].chartname;
            	var churi = dt[x].charturi;
            	
            	
            	if ( !hasDuplicatedEntry( ch, chartArray ) )
        		{
                	globals.chartArray.push(ch);
                    charts = charts+'<li id="'+ch+'" charturi="'+churi+'" class="ui-widget-content">'+ch+'</li>';
                    
                    chartArray.push(ch);
        		}
            	
            }
            getDimensions(); 
			$("#selectable3").html(charts);
    }, "json").error(function() {err("Error while showing supported charts."); });
    }

function getDimensions (){
	//console.log(decodeURIComponent(globals.dataset));
	$.post("/viz", { cmd: "getDimension",  dataset:decodeURIComponent(globals.dataset)},
	        function(dt) {
			
			globals.dimensionArray = dt;
			getMeasure();
			//console.log(globals.dimensionArray);
			globals.mappingArray = [];
			//globals.cachedChart = "";
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
	            /*if(dt.length == 1){
	            	//var chart = "";annel
	            	
                	var mappingObject = {'dim':dimension , 'dimensionuri':dimensionuri};
                	globals.mappingArray.push(mappingObject);
                
            		chart = globals.chartArray [0];
            		globals.cachedChart = chart;
            		//console.log (chart);
            		getVisualization();
              }*/
	            $("#selectable1").html(dimensions);
	        }, "json")
	        .error(function() {alert("Error while loading dimensions."); });
	}

function getMeasure(){
	globals.measure = "";
	$.post("/viz", { cmd: "getMeasure",  dataset:decodeURIComponent(globals.dataset)},
	        function(dt) {
			//globals.dimensionArray= dt;
			globals.mappingArray = [];
			//globals.cachedChart = "";
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

function getVisualization (){	
	console.log (globals.cubeComponentArray);
	var start=null; 
		 console.log (globals.cachedChart);
	
		 console.log(globals.cubeComponentArray);
		   //$("#vis").html("<img src='/static/images/ajax-loader.gif' border='0'>");
		    $.post("/viz", { cmd: "getVisualization", chart:globals.cachedChart, dataset:decodeURIComponent(globals.dataset), dimension:JSON.stringify(globals.cubeComponentArray)},
		    	
		        function(dt) {
		            var conf =  'var config={location:"vis", height:"600", width:"700", title:"Generated chart"}';
		            var warn = null;
		            $("#vis").html();
		            
		            $("#selectable4").html();
		            $("#demo2").html('');
		            
		            $("#demo2Up").html('');
		            $("#vis").html("<canvas id='background'></canvas><canvas id='foreground'></canvas>");		            

                    start = dt.start;
                    //console.log(start);
                    if(start==null){
                        alert("Chart  could not be generated");
                        return;
                    }
                    eval(conf);

                    console.log(start);
                    eval(start);
                    
                    globals.cubeComponentArray = [];

		        }, "json")
		        .error(function() {alert("Error while preparing preview."); });
	}


function getPossibleVisualizationVariants(){
	var nameArray = [];
	var channels = "";
	var nameString = "";
	var counter = 0;
	//console.log(globals.mappingInfoForVisualChannels);
	for (var i = 0;i<globals.mappingInfoForVisualChannels.length;i++){
		var object = globals.mappingInfoForVisualChannels[i];
		//console.log(object);
		var nameOfChart = object.chartname;
		//console.log(nameOfChart);

		if (nameOfChart == globals.cachedChart){
			
			var visualChannels = object.visualchannels;

			var channel = "";
			var chans = "";
			
			for (var l = 0; l<=(visualChannels.length-1);l++){

				var vis = visualChannels[l];
				//nsole.log(vis);	

				var name = vis.label;

				if (name !== "y-Axis"){
					chans = chans+'<option value="1" >'+name+'</optional>';
				}	
			}

			channel = channel+ '<select id="vischannel'+counter+'">'+chans+'</select>'  ;
			counter = counter +1;
			//console.log(channel);
			channels = channels+channel;
			//globals.mappingInfoForVisualChannels = [];
		}

	}
	if(globals.dimensionArray.length !=1){	

		$("#selectable4").html(channels);

	}
	sortingString(  );	
	getPossibleVisualizationVariantsAsString();
}

	
	
	
//-------------------------------------------------------------------------------
function getPossibleVisualizationVariantsAsString(){
	var nameArray = [];
	var channels = "";
	var nameString = "";
	
	var htmlString = "<font style=\"font-size:80%;\">";
	var cnt = 1;
	for (var i = 0;i<globals.mappingInfoForVisualChannels.length;i++){
		var object = globals.mappingInfoForVisualChannels[i];
		//console.log(object);
		var nameOfChart = object.chartname;
		//console.log(nameOfChart);

		if (nameOfChart == globals.cachedChart){
			
			var visualChannels = object.visualchannels;

			var channel = "";
			var chans = "";
			
			var htmlSuggestion = "";
			for (var l = 0; l<=(visualChannels.length-1);l++){

				var vis = visualChannels[l];
				//nsole.log(vis);	

				var name = vis.label;
				var componentObj = vis.component;
				var dataType = componentObj.datatype;
				var dimensionUri = componentObj.dimensionuri;
				var dimensionLabel = componentObj.label;
				var cubeDimUri = vis.name;
				var cubeDimLabel = vis.label;
				
				var currentSuggestionHtml =  
					"Datatype: "+dataType + "<br>"
					+ "Dimension URI: "+dimensionUri+"<br>"
					+ "Dimension: <b>"+dimensionLabel+"</b><br>"
					+ "Visual Channel URI: "+cubeDimUri+"<br>"
					+ "Visual Channel Label: <b>"+ cubeDimLabel+"</b><br>"
				htmlSuggestion = htmlSuggestion + currentSuggestionHtml+"<br>";
	
			}
			htmlString = htmlString+"<b>Suggestion Nr. "+(cnt)+"</b><hr>"+htmlSuggestion;
			cnt = cnt+1;
			
			
		}

	}
	$("#suggestions").html(htmlString);
}

function sortingString(  ){
	globals.cubeComponentArray = [];
	//console.log(globals.dimensionArray);
	for(var x = 0; x < globals.dimensionArray.length; x++){
    	//console.log (dt);
        var dimension = globals.dimensionArray[x].label;
        var dimensionuri = globals.dimensionArray[x].dimensionuri;
        var cubeComponent = getCubeComponent(dimensionuri);
        console.log(dimensionuri + "############"+cubeComponent);
        var cubeComponentObject = {'label':dimension, 'dimensionuri':dimensionuri, 'cubecomponent':cubeComponent, 'index': x}
        globals.cubeComponentArray.push(cubeComponentObject);
       
        $("#vischannel"+x).val(cubeComponent);
       
        
	}		
}

function getCubeComponent(dimensionuri){
	for (var i = 0;i<globals.mappingInfoForVisualChannels.length;i++){
		var object = globals.mappingInfoForVisualChannels[i];
		var visualChannels = object.visualchannels;
		var nameOfChart = object.chartname;
		//console.log("Hallo:" +nameOfChart+", : "+globals.cachedChart);

		var chans = "";
		
		if (nameOfChart == globals.cachedChart){
			//alert("JA")
			for (var l = 0; l<=(visualChannels.length-1);l++){
				chans = "";
				name = "";

				var vis = visualChannels[l];	

                var component = vis.component;
                var dimuri = component.dimensionuri ;
                if (dimensionuri == dimuri){
                    if (vis.chartname == globals.cachedChart){
                        return vis.label;
                    }
                }
                var mesuri = component.mesaureuri ;
                if (dimensionuri == mesuri){
                    if (vis.chartname == globals.cachedChart){
                        return vis.label;
                    }
                }
			}
		}
	}
	return ('undefined');
}
